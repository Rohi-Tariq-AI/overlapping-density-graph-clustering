# Validation Report: Version 1.1.0

Validation date: 2026-10-23

## Automated checks

- Python source compilation: passed.
- CLI help check: passed.
- Full pytest suite: **12 passed in 11.80 seconds**.
- Visualization unit and CLI integration tests: passed as part of the full suite.
- Existing public-release Football/Karate verification test: passed.
- Dolphins locked regression tests at target densities 0.40 and 0.60: passed.

## Dataset inspection

- Dolphins: 62 nodes, 159 edges, 95 triangles.
- Football: 115 nodes, 613 edges, 810 triangles.
- Karate: 34 nodes, 78 edges, 45 triangles.
- Les Miserables: 77 nodes, 254 edges, 467 triangles.
- Political Books: 105 nodes, 441 edges, 560 triangles.
- Power Grid: 4,941 nodes, 6,594 edges, 651 triangles.

All six GML datasets loaded as undirected and unweighted graphs.

## Dataset experiments at target density 0.40

Locked verification and visualization passed for:

- Dolphins: 5 clusters.
- Football: 12 clusters.
- Karate: 4 clusters.
- Les Miserables: 3 clusters.
- Political Books: 7 clusters.

Optimized execution passed for Power Grid:

- Power Grid: 173 clusters in 9.2145 seconds.

The additional locked-compatible Power Grid run was terminated by the execution environment with exit code 137 because running both implementations together exceeded available resources. This does not indicate an optimized-algorithm mismatch. Power Grid visualization was not generated because the requirement targets readable small and medium graphs and the dataset contains 4,941 nodes.

## Format handling

`FB.txt` and `aves-weaver-social-03.txt` are plain edge lists, not GML. They are retained under `data_edge_lists/` and are not silently converted or passed to the GML CLI.

## Algorithm preservation

SHA-256 comparison confirmed that `density.py`, `models.py`, `optimized.py`, `partitioning.py`, `quality.py`, `selection.py`, and `triangles.py` are byte-for-byte identical to the uploaded V2 files.
