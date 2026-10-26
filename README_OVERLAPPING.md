# Overlapping Graph Clustering With User-Specified Density

Release candidate `1.0.0rc1` for clique-based overlapping clustering.

## Method

Each cluster starts from a triangle containing no node from an earlier accepted cluster. The starting triangle is selected by the same average adjusted triangle-degree rule as partitioning clustering. After initialization, full-graph expansion is allowed, so final clusters may overlap.

Only relative density is used. Conductance is not used or reported.

## Command

```bash
pip install -e .
overlap-cluster data_gml/karate.gml --density 0.40 --output results/karate_040
```

Outputs: `results.json`, `clusters.csv`, and `summary.txt`.

## Validation

The automated suite reports `18 passed`. Fifteen multi-dataset experiments completed across Karate, dolphins, political books, Les Misérables, and football at densities 0.40, 0.50, and 0.60. Facebook remains a performance-validation gate and is documented in `validation/MULTIDATASET_VALIDATION_REPORT.md`.

## Final runtime validation

Version 1.0.0 was validated on eight datasets at target densities 0.40, 0.50, and 0.60. Across 24 experiments, overlapping clustering took a median 2.68x and mean 4.06x the optimized partitioning runtime. See `validation/FINAL_RUNTIME_VALIDATION_REPORT.md` and the CSV/JSON benchmark files for complete measurements.
