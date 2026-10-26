from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable
from pathlib import Path

import networkx as nx

from .density import normalized_edge, relative_density
from .models import ClusterResult, ClusteringResult, ClusterState, Edge, Node, Triangle
from .selection import select_average_candidate
from .triangles import adjusted_triangle_degree, find_triangles, triangle_edges


class PartitioningCliqueClusterer:
    """Triangle-seeded, density-guided partitioning clustering.

    Parameters
    ----------
    target_density:
        User-required density in the closed interval [0, 1].
    """

    def __init__(self, target_density: float, mode: str = "compatible", trace: bool = False):
        if not 0.0 <= target_density <= 1.0:
            raise ValueError("target_density must be between 0 and 1.")
        self.target_density = round(float(target_density), 2)
        if mode not in {"compatible", "corrected"}:
            raise ValueError("mode must be compatible or corrected")
        self.mode = mode
        self.trace = trace
        self.trace_lines: list[str] = []

    def fit(self, graph: nx.Graph) -> ClusteringResult:
        """Partition an undirected, unweighted graph."""
        if graph.is_directed():
            raise nx.NetworkXNotImplemented("Only undirected graphs are supported.")
        if nx.is_weighted(graph):
            raise ValueError("The current implementation expects an unweighted graph.")

        self.graph = graph.copy()
        self.node_order = {node: index for index, node in enumerate(self.graph.nodes())}
        self.node_degrees = dict(self.graph.degree())
        self.all_triangles = find_triangles(self.graph, mode=self.mode)
        self.triangle_order = {triangle: index for index, triangle in enumerate(self.all_triangles)}
        self.triangle_edge_map = {triangle: triangle_edges(triangle) for triangle in self.all_triangles}
        self.node_to_triangles = self._build_node_triangle_index(self.all_triangles)

        available = list(self.all_triangles)
        assigned_nodes: set[Node] = set()
        results: list[ClusterResult] = []

        while available:
            seed = self._select_triangle(available)
            best_state = self._expand_cluster(seed, available, assigned_nodes)
            results.append(self._to_result(best_state))

            # Partitioning rule: accepted nodes cannot appear in later clusters.
            assigned_nodes.update(best_state.nodes)
            available = [
                triangle
                for triangle in available
                if set(triangle).isdisjoint(assigned_nodes)
            ]

        unclustered = [node for node in self.graph.nodes() if node not in assigned_nodes]
        return ClusteringResult(
            clusters=tuple(results),
            unclustered_nodes=tuple(unclustered),
            target_density=self.target_density,
            triangle_count=len(self.all_triangles),
        )

    def write_trace(self, path: str) -> None:
        Path(path).write_text("\n".join(self.trace_lines), encoding="utf-8")

    def _build_node_triangle_index(
        self,
        triangles: list[Triangle],
    ) -> dict[Node, set[Triangle]]:
        index: dict[Node, set[Triangle]] = defaultdict(set)
        for triangle in triangles:
            for node in triangle:
                index[node].add(triangle)
        return index

    def _triangle_degree(self, triangle: Triangle) -> int:
        return adjusted_triangle_degree(triangle, self.node_degrees)

    def _select_triangle(self, candidates: list[Triangle]) -> Triangle:
        ordered = sorted(candidates, key=self.triangle_order.__getitem__)
        selected, index, degrees, average = select_average_candidate(ordered, self._triangle_degree, self.mode)
        if self.trace:
            self.trace_lines.extend([f"Candidates: {ordered}", f"Degrees: {degrees}; average: {average}", f"Selected index: {index}; selected: {selected}"])
        return selected

    def _expand_cluster(
        self,
        seed: Triangle,
        available_triangles: list[Triangle],
        forbidden_nodes: set[Node],
    ) -> ClusterState:
        if self.trace:
            self.trace_lines.append(f"Seed triangle: {seed}")
        state = ClusterState(
            nodes=set(seed),
            internal_edges=set(self.triangle_edge_map[seed]),
            used_triangles={seed},
            relative_density=0.0,
        )
        # Maintain incident edges incrementally. Rebuilding them from every
        # cluster node at every step is quadratic on large sparse graphs.
        incident_edges: set[Edge] = set()
        for node in state.nodes:
            incident_edges.update(
                normalized_edge(node, neighbor)
                for neighbor in self.graph.neighbors(node)
            )
        state.external_edges = incident_edges - state.internal_edges
        denominator = len(state.internal_edges) + len(state.external_edges)
        state.relative_density = round(
            len(state.internal_edges) / denominator if denominator else 0.0,
            2,
        )
        # Keep only the first state with the smallest deviation seen so far.
        # This is exactly equivalent to min(history, key=...) with stable
        # first-tie behavior, but avoids quadratic memory growth on large
        # graphs where thousands of expansion states may be visited.
        best_state = state.copy()
        best_difference = abs(state.relative_density - self.target_density)
        available_set = set(available_triangles)

        while state.relative_density != self.target_density:
            before_nodes = set(state.nodes)
            triangle = self._next_triangle(state, available_set, forbidden_nodes)
            if triangle is not None:
                before_edges = set(state.internal_edges)
                state.nodes.update(triangle)
                state.internal_edges.update(self.triangle_edge_map[triangle])
                state.used_triangles.add(triangle)
                if self.trace:
                    self.trace_lines.extend([f"Triangle expansion: {triangle}", f"New nodes: {sorted(state.nodes-before_nodes)}", f"New internal edges: {len(state.internal_edges-before_edges)}"])
            else:
                edge = self._next_single_edge(state, forbidden_nodes)
                if edge is None:
                    break
                state.internal_edges.add(edge)
                state.nodes.update(edge)

            new_nodes = state.nodes - before_nodes if triangle is not None else state.nodes - before_nodes
            for node in new_nodes:
                incident_edges.update(
                    normalized_edge(node, neighbor)
                    for neighbor in self.graph.neighbors(node)
                )
            state.external_edges = incident_edges - state.internal_edges
            denominator = len(state.internal_edges) + len(state.external_edges)
            state.relative_density = round(
                len(state.internal_edges) / denominator if denominator else 0.0,
                2,
            )
            difference = abs(state.relative_density - self.target_density)
            if difference < best_difference:
                best_state = state.copy()
                best_difference = difference
            if self.trace:
                self.trace_lines.append(f"State: nodes={sorted(state.nodes)}, internal={len(state.internal_edges)}, external={len(state.external_edges)}, RD={state.relative_density:.2f}")

        # Strict improvement preserves the original first-minimum tie rule.
        return best_state

    def _next_triangle(
        self,
        state: ClusterState,
        available_triangles: set[Triangle],
        forbidden_nodes: set[Node],
    ) -> Triangle | None:
        # Indexed candidate retrieval: only triangles incident to a current
        # cluster node can share 1, 2, or 3 nodes with the cluster. This avoids
        # scanning the complete triangle list after every expansion step while
        # preserving the original deterministic ordering and tie handling.
        incident_candidates: set[Triangle] = set()
        for node in state.nodes:
            incident_candidates.update(self.node_to_triangles.get(node, ()))

        candidates = incident_candidates.intersection(available_triangles)
        candidates.difference_update(state.used_triangles)
        if forbidden_nodes:
            candidates = {
                triangle
                for triangle in candidates
                if set(triangle).isdisjoint(forbidden_nodes)
            }
        if not candidates:
            return None

        grouped: dict[int, list[Triangle]] = {3: [], 2: [], 1: []}
        for triangle in candidates:
            common = sum(node in state.nodes for node in triangle)
            if common:
                grouped[common].append(triangle)

        for common_count in (3, 2, 1):
            if grouped[common_count]:
                return self._select_triangle(grouped[common_count])
        return None

    def _next_single_edge(
        self,
        state: ClusterState,
        forbidden_nodes: set[Node],
    ) -> Edge | None:
        candidates: list[tuple[Node, Node]] = []
        seen: set[Edge] = set()

        # Match the original notebook: consider every unrecorded graph edge
        # incident to the current cluster. The other endpoint may be outside
        # the cluster, or it may already be a cluster node whose connecting
        # edge has not yet been recorded as internal.
        for cluster_node in sorted(state.nodes, key=self.node_order.__getitem__):
            for other_node in self.graph.neighbors(cluster_node):
                if other_node in forbidden_nodes:
                    continue
                edge = normalized_edge(cluster_node, other_node)
                if edge in state.internal_edges or edge in seen:
                    continue
                seen.add(edge)
                candidates.append((cluster_node, other_node))

        if not candidates:
            return None

        def edge_degree(edge: tuple[Node, Node]) -> int:
            u, v = edge
            return self.node_degrees[u] + self.node_degrees[v] - 1

        selected, index, degrees, average = select_average_candidate(candidates, edge_degree, self.mode)
        if self.trace:
            self.trace_lines.extend([f"Edge candidates: {candidates}", f"Edge degrees: {degrees}; average: {average}", f"Selected edge index: {index}; selected: {selected}"])
        return normalized_edge(*selected)

    def _edge_tuple(self, edge: Edge) -> tuple[Node, Node]:
        return tuple(sorted(edge, key=self.node_order.__getitem__))  # type: ignore[return-value]

    def _to_result(self, state: ClusterState) -> ClusterResult:
        ordered_nodes = tuple(sorted(state.nodes, key=self.node_order.__getitem__))
        internal = tuple(sorted((self._edge_tuple(e) for e in state.internal_edges), key=lambda e: (self.node_order[e[0]], self.node_order[e[1]])))
        external = tuple(sorted((self._edge_tuple(e) for e in state.external_edges), key=lambda e: (self.node_order[e[0]], self.node_order[e[1]])))
        triangles = tuple(sorted(state.used_triangles, key=self.triangle_order.__getitem__))
        return ClusterResult(
            nodes=ordered_nodes,
            internal_edges=internal,
            external_edges=external,
            relative_density=state.relative_density,
            used_triangles=triangles,
        )
