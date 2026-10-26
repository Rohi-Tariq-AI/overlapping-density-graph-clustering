# User-Specified-Density Graph Clustering

Version **1.1.0** is a release-ready Python implementation of triangle-based partitioning graph clustering for simple, undirected, unweighted graphs. Users select one or more **target densities**, and the software returns disjoint clusters, quality metrics, structured outputs, optional traces, locked-result verification, and optional PNG visualizations.

> **Algorithm-preservation statement:** Version 1.1.0 does not modify triangle discovery, triangle ordering, candidate selection, cluster initialization, expansion, stopping conditions, node assignment, edge accounting, relative-density calculations, cluster order, quality formulas, unclustered-node calculation, or locked regression signatures. Visualization runs only after clustering finishes.

## Key features

- One or multiple GML datasets
- One or multiple target densities
- Compatible locked backend and optimized backend
- CSV, JSON, text summary, optional trace, and combined reports
- **Mean Relative Density Deviation Coefficient (MRDDC)**
- Average relative density and recorded-edge coverage
- Deterministic, headless cluster visualization
- Locked-reference verification and automated regression tests

## Installation

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Five-minute quick start

```bash
graph-cluster --graphs data_gml/dolphins.gml --densities 0.50 --visualize
```

Multiple densities:

```bash
graph-cluster --graphs data_gml/dolphins.gml --densities 0.25 0.40 0.50 0.70 0.90 --visualize
```

Multiple datasets:

```bash
graph-cluster --graphs data_gml/dolphins.gml data_gml/karate.gml --densities 0.40 0.60 --visualize
```

## Expected output

```text
results/dolphins/density_050/
├── clusters.csv
├── results.json
├── summary.txt
├── trace.txt                  # only with --trace
└── cluster_visualization.png  # only with --visualize
```

## Quality metrics

- **Relative density:** density achieved by one discovered cluster.
- **Average relative density:** mean relative density of all discovered clusters.
- **Mean Relative Density Deviation Coefficient (MRDDC):** agreement between target density and cluster relative densities. Values near 1.00 indicate close agreement.
- **Recorded-edge coverage:** proportion of graph edges recorded as internal cluster edges. It is not induced-subgraph coverage.

## Tests

```bash
python -m pytest
```

See [USER_GUIDE.md](USER_GUIDE.md) for full installation, dataset preparation, CLI, outputs, metrics, troubleshooting, reproducibility, and release guidance.

## Citation and attribution

Use the scholarly citation in [CITATION.md](CITATION.md) and preserve [ATTRIBUTION.md](ATTRIBUTION.md).

## License

Distributed under the project-specific license included in `LICENSE`. Redistribution and derivative works must preserve the required attribution and scholarly citation. This is not the MIT License.

## Release

Current version: **1.1.0**. See [CHANGELOG.md](CHANGELOG.md).
