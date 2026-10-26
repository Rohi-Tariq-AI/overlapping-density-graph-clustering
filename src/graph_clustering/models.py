from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable

Node = Hashable
Edge = frozenset[Node]
Triangle = tuple[Node, Node, Node]


@dataclass
class ClusterState:
    """One intermediate state in a cluster expansion."""

    nodes: set[Node]
    internal_edges: set[Edge]
    used_triangles: set[Triangle]
    relative_density: float
    external_edges: set[Edge] = field(default_factory=set)

    def copy(self) -> "ClusterState":
        return ClusterState(
            nodes=set(self.nodes),
            internal_edges=set(self.internal_edges),
            used_triangles=set(self.used_triangles),
            relative_density=self.relative_density,
            external_edges=set(self.external_edges),
        )


@dataclass(frozen=True)
class ClusterResult:
    """Final selected state for one partitioning cluster."""

    nodes: tuple[Node, ...]
    internal_edges: tuple[tuple[Node, Node], ...]
    external_edges: tuple[tuple[Node, Node], ...]
    relative_density: float
    used_triangles: tuple[Triangle, ...]


@dataclass(frozen=True)
class ClusteringResult:
    """Complete partitioning result."""

    clusters: tuple[ClusterResult, ...]
    unclustered_nodes: tuple[Node, ...]
    target_density: float
    triangle_count: int
