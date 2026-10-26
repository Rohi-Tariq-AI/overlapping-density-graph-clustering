# Prototype Validation Report

## Status

Initial implementation completed and tested.

## Scientific rule implemented

1. Cluster 1 uses the same selection and expansion methodology as partitioning clustering.
2. Every later starting triangle is node-disjoint from the union of all earlier accepted clusters.
3. Starting-triangle selection uses the same average adjusted triangle-degree rule.
4. After initialization, expansion uses the complete graph, so final clusters may overlap.
5. Only relative density is used. Conductance is not stored or reported.

## Automated tests

```text
17 passed
```

The suite includes five overlapping-specific tests plus the existing partitioning regression tests.

## Karate Club, target density 0.40

```text
Cluster 1
start: (0, 3, 7)
nodes: (0, 1, 3, 7, 12, 13, 17)
internal: 13
external: 18
relative density: 0.42

Cluster 2
start: (2, 8, 32)
nodes: (0, 1, 2, 3, 7, 8, 13, 17, 32)
internal: 20
external: 29
relative density: 0.41

Cluster 3
start: (33, 29, 26)
nodes: (30, 27, 32, 33, 14, 23, 29, 26)
internal: 14
external: 22
relative density: 0.39

Cluster 4
start: (31, 25, 24)
nodes: (31, 30, 28, 32, 33, 14, 15, 18, 25, 24)
internal: 16
external: 22
relative density: 0.42

Cluster 5
start: (5, 6, 16)
nodes: (0, 4, 5, 6, 10, 16)
internal: 9
external: 13
relative density: 0.41
```

Overlapping nodes:

```text
(0, 1, 3, 7, 13, 17, 30, 32, 33, 14)
```

Unclustered nodes:

```text
(11, 19, 21, 9, 20, 22)
```

## Confirmed invariants

- Cluster 1 equals partitioning Cluster 1.
- All later starts are disjoint from earlier accepted clusters.
- Overlap occurs only after cluster initialization.
- Every stored density matches its internal and external edge counts.
- The input graph remains unchanged.

## Important interpretation

Clusters 2 onward intentionally differ from the rough notebook where a later starting triangle could contain nodes from an earlier cluster. The prototype follows the clarified scientific methodology rather than preserving that rough-code defect.

## Next work

- compare multiple datasets and target densities;
- add overlapping-specific CSV and JSON serialization;
- add trace output for eligible starting triangles;
- add overlapping visualization;
- add CLI mode;
- prepare public documentation only after multi-dataset validation.
