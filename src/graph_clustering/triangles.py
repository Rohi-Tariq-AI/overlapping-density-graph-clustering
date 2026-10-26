from __future__ import annotations

import networkx as nx

from .models import Node, Triangle


def find_triangles_compatible(graph: nx.Graph) -> list[Triangle]:
    """Preserve enumerate_all_cliques triangle order but stop before larger cliques."""
    triangles: list[Triangle] = []
    for clique in nx.enumerate_all_cliques(graph):
        if len(clique) == 3:
            triangles.append(tuple(clique))
        elif len(clique) > 3:
            break
    return triangles


def find_triangles_fast(graph: nx.Graph) -> list[Triangle]:
    """Find every triangle once using neighbor intersections."""
    order = {node: index for index, node in enumerate(graph.nodes())}
    neighbors = {node: set(graph.neighbors(node)) for node in graph.nodes()}
    triangles: list[Triangle] = []
    for u in graph.nodes():
        for v in neighbors[u]:
            if order[u] >= order[v]:
                continue
            for w in neighbors[u].intersection(neighbors[v]):
                if order[v] < order[w]:
                    triangles.append((u, v, w))
    triangles.sort(key=lambda tri: tuple(order[node] for node in tri))
    return triangles


def find_triangles(graph: nx.Graph, mode: str = "compatible") -> list[Triangle]:
    if mode == "compatible":
        return find_triangles_compatible(graph)
    if mode == "corrected":
        return find_triangles_fast(graph)
    raise ValueError("mode must be 'compatible' or 'corrected'")


def triangle_edges(triangle: Triangle) -> set[frozenset[Node]]:
    u, v, w = triangle
    return {frozenset((u, v)), frozenset((u, w)), frozenset((v, w))}


def adjusted_triangle_degree(triangle: Triangle, node_degrees: dict[Node, int]) -> int:
    return sum(node_degrees[node] for node in triangle) - 3
