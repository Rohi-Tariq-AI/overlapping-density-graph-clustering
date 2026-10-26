from __future__ import annotations

import networkx as nx

from .models import Edge, Node


def normalized_edge(u: Node, v: Node) -> Edge:
    """Represent an undirected edge independently of endpoint order."""
    return frozenset((u, v))


def external_edges(
    graph: nx.Graph,
    cluster_nodes: set[Node],
    internal_edges: set[Edge],
) -> set[Edge]:
    """Return incident graph edges not yet recorded as internal.

    This intentionally does not replace the internal-edge set with the induced
    subgraph. Internal edges enter the cluster only through selected triangles
    or selected single edges.
    """
    incident: set[Edge] = set()
    for node in cluster_nodes:
        incident.update(normalized_edge(node, neighbor) for neighbor in graph.neighbors(node))
    return incident - internal_edges


def relative_density(
    graph: nx.Graph,
    cluster_nodes: set[Node],
    internal_edges: set[Edge],
) -> tuple[float, set[Edge]]:
    """Calculate |E_internal| / (|E_internal| + |E_external|)."""
    outside = external_edges(graph, cluster_nodes, internal_edges)
    denominator = len(internal_edges) + len(outside)
    value = len(internal_edges) / denominator if denominator else 0.0
    return round(value, 2), outside
