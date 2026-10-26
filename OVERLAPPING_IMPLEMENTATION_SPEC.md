# Overlapping Graph Clustering With User-Specified Density

## Implementation Specification

## 1. Purpose

Develop a reproducible Python implementation of the clique-based overlapping graph-clustering algorithm by preserving the validated partitioning-clustering methodology and introducing overlap only where required by the original overlapping implementation.

## 2. Scientific invariants retained from partitioning clustering

The overlapping implementation must preserve:

1. input validation for simple, connected, undirected, unweighted graphs;
2. exhaustive triangle discovery;
3. adjusted-degree calculation for triangles;
4. average-degree selection and deterministic tie handling;
5. triangle-priority expansion by the number of nodes shared with the current cluster;
6. relative density as the density-monitoring quantity;
7. for the first cluster, continue the established initial expansion until its accepted relative density equals the user-specified target density; for later clusters, preserve the original candidate-selection rule when an exact value is not attainable;
8. MRDDC-based evaluation;
9. deterministic results, structured outputs, tests, and optional visualization.

## 3. Overlapping rule

The two triangle collections must be kept separate.

### 3.1 Eligible starting triangles

A new cluster must begin from a unique, unused triangle.

After a cluster is accepted, every triangle represented as used within the accepted cluster state is removed from eligibility as a future starting triangle.

### 3.2 Expansion triangles

The full graph and its triangle structures remain available when expanding later clusters. Previously clustered nodes are not removed from the graph. Consequently:

- nodes may belong to multiple clusters;
- edges may be internal to multiple clusters;
- expansion structures may overlap across clusters;
- accepted clusters are not required to be node-disjoint.

### 3.3 Formal state

The implementation must maintain:

- `all_triangles`: complete deterministic triangle list used for expansion;
- `eligible_start_triangles`: triangles still permitted to initialize a cluster;
- `used_start_structure`: triangles consumed by accepted cluster states and therefore unavailable for future initialization.

## 4. Main algorithm

1. Validate and copy the input graph.
2. Enumerate and deterministically order all triangles.
3. Initialize `eligible_start_triangles` with all triangles.
4. While eligible starting triangles remain:
   1. choose the average-adjusted-degree triangle from the eligible pool;
   2. initialize a new cluster state from that triangle;
   3. expand using the complete expansion-triangle collection;
   4. prioritize candidates sharing three, then two, then one node with the current cluster, preserving original average-degree ordering;
   5. use eligible single edges only when no triangle candidate is available, preserving the original fallback behavior;
   6. record every intermediate state and relative density;
   7. select the first intermediate state with minimum absolute deviation from the target density;
   8. save the accepted cluster;
   9. remove the accepted state's used triangles from `eligible_start_triangles` only;
   10. leave graph nodes and graph edges available for later expansion.
5. Calculate overlap-aware experiment metrics.


## 4.1 First-cluster density invariant

The first accepted cluster is a special methodological invariant: its relative density must equal the user-specified target density after the algorithm's stated rounding convention. For target density `0.40`, Cluster 1 must therefore report `0.40`, not `0.42`.

The rough notebook output `0.42` must not be locked into the new regression suite. It indicates that the rough implementation selected the nearest recorded intermediate state, stopped at a non-reference state, or mixed state/edge accounting during return. The reconstruction phase must trace every first-cluster intermediate state and determine the exact point at which relative density reaches the target.

Acceptance rule for Cluster 1:

`round(cluster_relative_density, 2) == round(target_density, 2)`

If no exact first-cluster state is produced, the implementation must raise a validation discrepancy rather than silently accept the nearest value.

## 5. Required result model

Each cluster result must record:

- cluster number;
- starting triangle;
- ordered node membership;
- triangles used in the accepted state;
- internal edges;
- external edges;
- relative density;
- absolute and normalized deviation from target density.

The complete experiment must record:

- cluster count;
- starting-triangle sequence;
- overlapping nodes and their cluster memberships;
- overlapping edges and their cluster memberships;
- unclustered nodes based on the union of clustered nodes;
- average relative density;
- MRDDC;
- unique edge coverage;
- membership-weighted edge coverage;
- runtime;
- graph and triangle counts.

## 6. Metric corrections

### Unclustered nodes

Calculate from set union:

`graph_nodes - union(cluster_nodes)`

Do not subtract the sum of cluster sizes, because overlapping nodes appear more than once.

### Edge coverage

Report two separate quantities:

1. unique edge coverage, bounded by 0 and 1;
2. membership-weighted edge coverage, which may exceed 1 because an edge can be internal to multiple clusters.

### MRDDC

Use the same target-density deviation formulation as the partitioning release, applied to accepted overlapping clusters.

## 7. Compatibility reference

The initial regression reference is the recorded Karate Club run at target density 0.40:

- graph nodes: 34;
- graph edges: 78;
- triangles: 45;
- accepted clusters: 5;
- required first-cluster relative density: 0.40, exactly equal to the target density;
- the saved rough-notebook value of 0.42 is treated as a divergence to investigate, not as the reference value;
- later cluster densities must be reconstructed and validated from the intended methodology and original expansion sequence.

Recorded clusters:

1. `[0, 1, 3, 7, 12, 13, 17]`
2. `[32, 33, 2, 0, 8, 14, 15, 18, 20, 23, 29, 30]`
3. `[0, 1, 2, 3, 7, 13, 21]`
4. `[0, 1, 2, 3, 4, 5, 6, 7, 8, 32, 10, 11, 16, 19]`
5. `[32, 33, 22, 23, 24, 25, 26, 27, 28, 29, 31]`

Recorded overlapping nodes:

`0, 1, 2, 3, 7, 8, 13, 23, 29, 32, 33`

## 8. Validation stages

### Stage A: Compatibility implementation

Reproduce the original notebook's ordering and accepted Karate result without global state.

### Stage B: Correctness checks

Correct reporting defects that do not alter cluster selection, including negative unclustered-node counts and ambiguous edge coverage.

### Stage C: Multi-dataset regression

Run the same datasets and target-density values used for the partitioning release, then compare deterministic signatures.

### Stage D: Public software packaging

Provide CLI, CSV/JSON/text outputs, trace mode, visualization, documentation, tests, package metadata, citation, attribution, and release checklist.

## 9. Required tests

1. deterministic triangle ordering;
2. deterministic average-degree start selection;
3. every accepted cluster has a unique starting triangle;
4. no consumed start triangle is selected again;
5. nodes may appear in multiple clusters;
6. overlapping memberships are reported correctly;
7. input graph is not modified;
8. relative density and MRDDC are correct;
9. unclustered nodes use union semantics;
10. unique edge coverage is bounded by 1;
11. regression for Karate at 0.40, including the invariant that Cluster 1 relative density equals 0.40 exactly;
12. arbitrary and string node labels;
13. invalid graph handling;
14. repeated runs produce identical results.

## 10. Implementation boundary

The first public overlapping release will implement the clique-based method represented by the supplied original notebook. It will not be described as the edge-based overlapping algorithm unless the edge-based source is separately supplied and validated.
