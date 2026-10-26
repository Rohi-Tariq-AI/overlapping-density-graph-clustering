from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

import networkx as nx

from .models import ClusterResult, ClusterState, Node, Triangle
from .optimized import OptimizedPartitioningCliqueClusterer
from .triangles import find_triangles, triangle_edges


@dataclass(frozen=True)
class OverlappingClusterResult:
    """One accepted overlapping cluster and its initialization triangle."""

    starting_triangle: Triangle
    nodes: tuple[Node, ...]
    internal_edges: tuple[tuple[Node, Node], ...]
    external_edges: tuple[tuple[Node, Node], ...]
    relative_density: float
    used_triangles: tuple[Triangle, ...]


@dataclass(frozen=True)
class OverlappingClusteringResult:
    """Complete result of clique-based overlapping clustering."""

    clusters: tuple[OverlappingClusterResult, ...]
    overlapping_nodes: tuple[Node, ...]
    unclustered_nodes: tuple[Node, ...]
    target_density: float
    triangle_count: int


class OverlappingCliqueClusterer(OptimizedPartitioningCliqueClusterer):
    """Triangle-seeded overlapping clustering with user-specified density.

    The expansion procedure is intentionally inherited from
    :class:`OptimizedPartitioningCliqueClusterer`. The difference begins only after an
    accepted cluster:

    * the next starting triangle must contain no node from any previously
      accepted cluster;
    * once that disjoint starting triangle is selected, expansion again uses
      the full graph and all triangles, so previously clustered nodes may be
      included and final clusters may overlap.
    """

    def fit(self, graph: nx.Graph) -> OverlappingClusteringResult:
        if graph.is_directed():
            raise nx.NetworkXNotImplemented("Only undirected graphs are supported.")
        if nx.is_weighted(graph):
            raise ValueError("The current implementation expects an unweighted graph.")

        self.graph = graph.copy()
        self._neighbor_position = {
            (u, v): index
            for u in self.graph.nodes()
            for index, v in enumerate(self.graph.neighbors(u))
        }
        self.node_order = {node: index for index, node in enumerate(self.graph.nodes())}
        self.node_degrees = dict(self.graph.degree())
        self.all_triangles = find_triangles(self.graph, mode=self.mode)
        self.triangle_order = {
            triangle: index for index, triangle in enumerate(self.all_triangles)
        }
        self.triangle_edge_map = {
            triangle: triangle_edges(triangle) for triangle in self.all_triangles
        }
        self.node_to_triangles = self._build_node_triangle_index(self.all_triangles)

        covered_start_nodes: set[Node] = set()
        results: list[OverlappingClusterResult] = []

        while True:
            eligible_starts = [
                triangle
                for triangle in self.all_triangles
                if set(triangle).isdisjoint(covered_start_nodes)
            ]
            if not eligible_starts:
                break

            seed = self._select_triangle(eligible_starts)

            # Overlapping rule: after the disjoint seed is chosen, expansion
            # can use every graph triangle and every graph node.
            best_state = self._expand_cluster(
                seed,
                self.all_triangles,
                set(),
            )
            base_result = self._to_result(best_state)
            results.append(self._with_starting_triangle(seed, base_result))

            # This set is used only to filter future starting triangles. It is
            # deliberately not used during expansion.
            covered_start_nodes.update(best_state.nodes)

        clustered_union: set[Node] = set()
        membership_count: dict[Node, int] = {node: 0 for node in self.graph.nodes()}
        for cluster in results:
            clustered_union.update(cluster.nodes)
            for node in cluster.nodes:
                membership_count[node] += 1

        overlapping_nodes = tuple(
            node for node in self.graph.nodes() if membership_count[node] > 1
        )
        unclustered_nodes = tuple(
            node for node in self.graph.nodes() if node not in clustered_union
        )

        self._validate_starting_triangles(results)
        self._validate_density_consistency(results)

        return OverlappingClusteringResult(
            clusters=tuple(results),
            overlapping_nodes=overlapping_nodes,
            unclustered_nodes=unclustered_nodes,
            target_density=self.target_density,
            triangle_count=len(self.all_triangles),
        )

    def _with_starting_triangle(
        self,
        seed: Triangle,
        cluster: ClusterResult,
    ) -> OverlappingClusterResult:
        return OverlappingClusterResult(
            starting_triangle=seed,
            nodes=cluster.nodes,
            internal_edges=cluster.internal_edges,
            external_edges=cluster.external_edges,
            relative_density=cluster.relative_density,
            used_triangles=cluster.used_triangles,
        )

    @staticmethod
    def _validate_starting_triangles(
        clusters: list[OverlappingClusterResult],
    ) -> None:
        earlier_nodes: set[Node] = set()
        for cluster in clusters:
            if not set(cluster.starting_triangle).isdisjoint(earlier_nodes):
                raise AssertionError(
                    "A starting triangle contains a node from an earlier cluster: "
                    f"{cluster.starting_triangle}"
                )
            earlier_nodes.update(cluster.nodes)

    @staticmethod
    def _validate_density_consistency(
        clusters: list[OverlappingClusterResult],
    ) -> None:
        for cluster in clusters:
            denominator = len(cluster.internal_edges) + len(cluster.external_edges)
            recalculated = (
                round(len(cluster.internal_edges) / denominator, 2)
                if denominator
                else 0.0
            )
            if recalculated != cluster.relative_density:
                raise AssertionError(
                    "Selected state has inconsistent relative density: "
                    f"stored={cluster.relative_density}, recalculated={recalculated}"
                )
