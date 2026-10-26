# Final Eight-Dataset Runtime Validation

## Experimental design

Both methods used the same optimized indexed backend and corrected exact triangle enumeration. Each graph was loaded once per benchmark process, self-loops were removed, and each method was timed independently at target densities 0.40, 0.50, and 0.60.

The comparison covers Karate, dolphins, football, political books, Les Misérables, power grid, Facebook, and the Weaver bird social network.

## Scientific invariants

- First-cluster equality passed in all 24 experiments.
- The disjoint starting-triangle rule passed in all 24 overlapping experiments.
- The automated regression suite reports 18 passing tests.
- No conductance calculation is included.

## Runtime interpretation

Across all experiments, overlapping clustering required a median of **2.67x** and a mean of **4.06x** the partitioning runtime.
The observed range was **1.20x to 12.09x**.

This is an expected methodological cost: partitioning removes assigned nodes from later expansion, whereas overlapping clustering retains the full graph for later expansion and therefore evaluates more reusable nodes, edges, and triangle relationships.

## Measured runtimes

| Dataset | Density | Nodes | Edges | Partitioning s | Overlapping s | Ratio | P clusters | O clusters |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| karate | 0.40 | 34 | 78 | 0.004 | 0.009 | 2.24x | 4 | 5 |
| karate | 0.50 | 34 | 78 | 0.003 | 0.008 | 2.71x | 3 | 3 |
| karate | 0.60 | 34 | 78 | 0.002 | 0.006 | 2.36x | 3 | 4 |
| dolphins | 0.40 | 62 | 159 | 0.010 | 0.012 | 1.20x | 5 | 6 |
| dolphins | 0.50 | 62 | 159 | 0.012 | 0.057 | 4.77x | 4 | 5 |
| dolphins | 0.60 | 62 | 159 | 0.005 | 0.009 | 2.03x | 3 | 4 |
| football | 0.40 | 115 | 613 | 0.096 | 0.293 | 3.06x | 11 | 14 |
| football | 0.50 | 115 | 613 | 0.095 | 0.198 | 2.09x | 10 | 11 |
| football | 0.60 | 115 | 613 | 0.082 | 0.118 | 1.43x | 4 | 6 |
| polbooks | 0.40 | 105 | 441 | 0.058 | 0.140 | 2.41x | 5 | 10 |
| polbooks | 0.50 | 105 | 441 | 0.074 | 0.304 | 4.09x | 4 | 10 |
| polbooks | 0.60 | 105 | 441 | 0.116 | 0.297 | 2.56x | 5 | 7 |
| les_miserables | 0.40 | 77 | 254 | 0.022 | 0.086 | 3.99x | 3 | 6 |
| les_miserables | 0.50 | 77 | 254 | 0.100 | 0.135 | 1.34x | 3 | 4 |
| les_miserables | 0.60 | 77 | 254 | 0.079 | 0.130 | 1.63x | 3 | 4 |
| power | 0.40 | 4941 | 6594 | 10.146 | 25.216 | 2.49x | 173 | 175 |
| power | 0.50 | 4941 | 6594 | 1.198 | 6.918 | 5.77x | 123 | 135 |
| power | 0.60 | 4941 | 6594 | 0.383 | 1.009 | 2.63x | 80 | 79 |
| facebook | 0.40 | 620 | 2090 | 1.299 | 15.706 | 12.09x | 24 | 26 |
| facebook | 0.50 | 620 | 2090 | 1.712 | 15.993 | 9.34x | 20 | 19 |
| facebook | 0.60 | 620 | 2090 | 2.102 | 20.699 | 9.85x | 13 | 22 |
| aves_weaver | 0.40 | 42 | 152 | 0.010 | 0.079 | 8.20x | 5 | 6 |
| aves_weaver | 0.50 | 42 | 152 | 0.027 | 0.085 | 3.11x | 4 | 5 |
| aves_weaver | 0.60 | 42 | 152 | 0.014 | 0.087 | 6.11x | 5 | 5 |

## Large-graph results

Power grid completed at all densities. At 0.40, partitioning took 10.146 s and overlapping took 25.216 s. At 0.50, the times were 1.198 s and 6.918 s. At 0.60, the times were 0.383 s and 1.009 s.

Facebook completed at all densities. Partitioning ranged from 1.299 s to 2.102 s, while overlapping ranged from 15.706 s to 20.699 s.

## Optimization changes

1. Replaced full triangle-list scans during expansion with a node-to-triangle index.
2. Replaced complete expansion-history storage with streaming best-state retention, preserving the original first-minimum tie rule.
3. Maintained density state incrementally instead of rebuilding all incident edges after every step.
4. Reused the optimized edge and triangle expansion backend for overlapping clustering.

These changes preserve cluster selection and tie-breaking while making the power-grid and Facebook experiments practical.
