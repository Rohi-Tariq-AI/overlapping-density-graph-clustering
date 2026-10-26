# Clique-Based Overlapping Graph Clustering With User-Specified Density

## Frozen Methodology for the Clean Implementation

## 1. Shared first-cluster methodology

Partitioning and overlapping clustering use the same graph validation, triangle enumeration, adjusted triangle degree, average-degree triangle selection, candidate priorities, edge fallback, relative-density calculation, intermediate-state recording, and closest-density selection.

Therefore, for the same graph, node labels, triangle order, tie handling, and target density, Cluster 1 must be identical in both methods.

For Karate at target density 0.40, the validated zero-based reference is:

- starting triangle: `(0, 3, 7)`;
- cluster nodes: `(0, 1, 3, 7, 12, 13, 17)`;
- internal edges: 13;
- external edges: 18;
- relative density: 0.42.

## 2. Separation after an accepted cluster

Let `covered_start_nodes` be the union of the node memberships of all previously accepted clusters.

### Partitioning

Previously clustered nodes are unavailable for both future initialization and expansion.

### Overlapping

Previously clustered nodes are unavailable only when selecting the next starting triangle. They remain available during expansion.

## 3. Starting-triangle eligibility

For Cluster k > 1, a triangle is eligible to initialize the cluster only when it contains no node belonging to any previously accepted cluster.

Formal condition:

```python
set(triangle).isdisjoint(covered_start_nodes)
```

Example:

```text
Cluster 1 nodes = {2, 3, 4, 5, 6}
```

Invalid Cluster 2 starts:

```text
(2, 7, 8)
(3, 9, 10)
(4, 5, 11)
```

Valid Cluster 2 start:

```text
(7, 8, 9)
```

The valid starting triangle is then selected from the eligible set by the same average-adjusted-degree rule used in partitioning clustering.

## 4. Expansion eligibility

After the starting triangle is selected, expansion uses the complete graph and the original overlapping expansion logic. Triangles or edges containing nodes from previous clusters may participate in expansion.

This permits final cluster overlap while preserving a unique, previously uncovered starting region for every cluster.

## 5. Correct control flow

```python
all_triangles = find_triangles(graph)
accepted_clusters = []
covered_start_nodes = set()

while True:
    eligible_starts = [
        triangle
        for triangle in all_triangles
        if set(triangle).isdisjoint(covered_start_nodes)
    ]

    if not eligible_starts:
        break

    start_triangle = select_average_candidate(
        eligible_starts,
        adjusted_triangle_degree,
    )

    states = expand_cluster(
        graph=graph,
        starting_triangle=start_triangle,
        expansion_triangles=all_triangles,
        target_density=target_density,
    )

    accepted = select_closest_density_state(
        states,
        target_density,
    )

    accepted_clusters.append(accepted)
    covered_start_nodes.update(accepted.nodes)
```

The `covered_start_nodes` set is used only to choose a new starting triangle. It must not be used to prohibit nodes during expansion.

## 6. Relative density only

The algorithm uses:

```text
relative density = internal edges / (internal edges + external edges)
```

Conductance is not part of the clean implementation and will not be stored or reported.

Every accepted state must satisfy:

```python
round(
    len(state.internal_edges)
    / (len(state.internal_edges) + len(state.external_edges)),
    2,
) == state.relative_density
```

## 7. State integrity

Each intermediate state stores synchronized copies of:

- nodes;
- internal edges;
- external edges;
- used expansion triangles;
- relative density.

The clean implementation will not use separate parallel lists for these quantities.

## 8. Required invariants

1. Cluster 1 equals partitioning Cluster 1 for the same graph and density.
2. Every later starting triangle is disjoint from the union of all earlier accepted cluster nodes.
3. Later accepted clusters may overlap earlier accepted clusters after expansion.
4. Starting triangles are deterministic under the original average-degree selection rule.
5. Stored relative density equals the density recalculated from the selected state's edges.
6. The input graph is never modified.
7. Unclustered nodes are computed from the union of accepted cluster memberships.
8. Unique edge coverage is bounded by 1.0.

## 9. Karate 0.40 reference currently retained

The corrected original overlapping notebook produced:

- Cluster 1: `[0, 1, 3, 7, 12, 13, 17]`, density 0.42;
- Cluster 2: `[32, 33, 2, 0, 8, 14, 15, 18, 20, 23, 29, 30]`, density 0.40;
- Cluster 3: `[0, 1, 2, 3, 7, 13, 21]`, density 0.39;
- Cluster 4: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 32, 10, 11, 16, 19]`, density 0.40;
- Cluster 5: `[32, 33, 22, 23, 24, 25, 26, 27, 28, 29, 31]`, density 0.40.

Before locking Clusters 2-5 into regression tests, their starting triangles must be checked against the stricter disjoint-start invariant. Any original-notebook cluster whose starting triangle contains an earlier clustered node is evidence that the rough code did not fully enforce the intended methodology and must not be preserved as ground truth.

## 10. Development sequence

1. Reuse partitioning expansion code unchanged for Cluster 1.
2. Add the disjoint-start filter before every later start selection.
3. Keep the full graph available to expansion.
4. Record starting triangles explicitly.
5. Validate first-cluster equivalence.
6. Validate disjoint later starts.
7. Validate actual overlap after expansion.
8. Compare against the corrected original notebook and document intentional differences caused by enforcing the stated methodology.
