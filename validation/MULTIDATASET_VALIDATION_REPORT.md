# Multi-Dataset Validation Report

## Scope

Completed 15 experiments across five datasets and three target densities (0.40, 0.50, 0.60).

Validated datasets: Karate, dolphins, political books, Les Misérables, and football.

Facebook was attempted in corrected mode but did not complete within the 180-second validation limit. The release is therefore labeled **1.0.0rc1**, not a final 1.0.0 public release. This protects the scientific record from claiming validation that has not completed.

## Invariants

- First-cluster equivalence passed in all 15 completed experiments.
- Disjoint starting-triangle eligibility passed in all 15 completed experiments.
- Density-state consistency is enforced by the implementation and automated tests.
- The graph is copied before clustering and immutability tests pass.

## Automated test suite

```text
18 passed
```

## Completed experiment summary

| Dataset | Mode | Target | Clusters | Overlap nodes | Unclustered | ARD | MRDDC | Runtime s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dolphins | compatible | 0.40 | 6 | 7 | 26 | 0.40 | 0.99 | 0.034 |
| dolphins | compatible | 0.50 | 4 | 14 | 23 | 0.50 | 0.99 | 0.251 |
| dolphins | compatible | 0.60 | 4 | 36 | 19 | 0.60 | 1.00 | 0.082 |
| football | corrected | 0.40 | 14 | 31 | 7 | 0.40 | 1.00 | 2.378 |
| football | corrected | 0.50 | 11 | 41 | 5 | 0.50 | 1.00 | 2.648 |
| football | corrected | 0.60 | 6 | 50 | 0 | 0.60 | 1.00 | 1.415 |
| karate | compatible | 0.40 | 5 | 10 | 6 | 0.41 | 0.97 | 0.031 |
| karate | compatible | 0.50 | 3 | 6 | 5 | 0.49 | 0.97 | 0.055 |
| karate | compatible | 0.60 | 4 | 17 | 3 | 0.60 | 0.99 | 0.019 |
| les_miserables | compatible | 0.40 | 6 | 20 | 30 | 0.40 | 1.00 | 0.376 |
| les_miserables | compatible | 0.50 | 4 | 26 | 33 | 0.50 | 1.00 | 0.822 |
| les_miserables | compatible | 0.60 | 4 | 29 | 31 | 0.60 | 1.00 | 0.697 |
| polbooks | compatible | 0.40 | 10 | 45 | 21 | 0.40 | 1.00 | 0.806 |
| polbooks | compatible | 0.50 | 8 | 46 | 23 | 0.50 | 1.00 | 1.601 |
| polbooks | compatible | 0.60 | 8 | 63 | 13 | 0.60 | 1.00 | 2.060 |

## Facebook performance gate

The supplied Facebook edge list exceeded the 180-second execution limit even with corrected triangle enumeration. No Facebook result was simulated or substituted. Before a final 1.0.0 release, the expansion path must be optimized without changing selection order, and Facebook must pass the same invariants at all three densities.

## Release decision

The software is packaged as a reproducible **release candidate**. It is suitable for continued scientific validation, but it should not yet be described as fully finalized across all requested datasets.
