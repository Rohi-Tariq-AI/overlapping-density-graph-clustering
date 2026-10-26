# Overlapping Graph Clustering Prototype

This development prototype adds a clique-based overlapping clusterer to the
validated partitioning package.

## Frozen rule

- Cluster 1 uses exactly the partitioning methodology.
- Every later cluster starts from a triangle containing no node from any
  previously accepted cluster.
- The disjoint starting triangle is selected by the same average adjusted
  triangle-degree rule as partitioning clustering.
- After initialization, expansion uses the complete graph and may include
  nodes from earlier clusters.
- Conductance is not used or reported.

## Development status

This is an initial implementation for scientific validation, not a public
release. The current tests verify first-cluster equivalence, disjoint starting
triangles, overlap after expansion, density consistency, and graph immutability.
