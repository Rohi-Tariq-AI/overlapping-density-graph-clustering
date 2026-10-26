# Complete User Guide

## 1. Software overview and scientific purpose

This software discovers clusters in a simple, undirected, unweighted graph according to a user-selected **target density**. The validated V2 methodology starts from graph triangles and constructs node-disjoint clusters. Nodes not assigned to a discovered cluster are reported as **unclustered nodes**. Visualization is optional post-processing and never participates in discovery, selection, expansion, stopping, or metric calculation.

## 2. Main features

- GML datasets; one or many datasets per command
- One or many target-density values
- Cluster membership and edge-accounting outputs
- CSV, JSON, summary, optional trace, and combined reports
- Locked-reference verification
- Deterministic, headless PNG visualization
- Regression and visualization tests

## 3. System requirements

- Python 3.10 or newer
- NetworkX 3.x
- Matplotlib 3.8 or newer, below 4.0
- pytest 8 or newer for testing
- A writable output directory

## 4. Installation from source

Create a virtual environment.

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

`-e` means editable installation: changes to the source package are used without reinstalling it. Dependencies can alternatively be installed with:

```bash
python -m pip install -r requirements.txt
```

## 5. Project folder structure

```text
src/graph_clustering/  package source
tests/                 automated tests
data_gml/              supported GML datasets
data_edge_lists/       supplied reference edge lists; not accepted by the GML CLI
results/                generated outputs
README.md               project landing page
USER_GUIDE.md           complete instructions
RELEASE_CHECKLIST.md    verified release status
```

The compatibility folder `data/` contains Football and Karate GML files using their historical `.txt` names because the existing public-release test references those paths.

## 6. Supported dataset format

The CLI accepts GML content in `.gml` or `.txt` files. A minimal graph is:

```text
graph [
  directed 0
  node [ id 1 label "A" ]
  node [ id 2 label "B" ]
  edge [ source 1 target 2 ]
]
```

Requirements:

- graph must be undirected;
- graph must be unweighted for the validated V2 algorithm;
- graph must not be empty;
- node identifiers must be unique;
- edge endpoints must reference existing nodes;
- integer, nonconsecutive integer, and string labels can be visualized.

`FB.txt` and `aves-weaver-social-03.txt` are plain edge lists and are stored under `data_edge_lists/`. They are not silently converted because the validated public CLI supports GML datasets.

## 7. Quick start and command examples

One dataset and one target density:

```bash
graph-cluster --graphs data_gml/dolphins.gml --densities 0.50
```

One dataset and multiple target densities:

```bash
graph-cluster --graphs data_gml/dolphins.gml --densities 0.25 0.40 0.50 0.70 0.90
```

Multiple datasets and one target density:

```bash
graph-cluster --graphs data_gml/dolphins.gml data_gml/karate.gml --densities 0.40
```

Multiple datasets and multiple target densities:

```bash
graph-cluster --graphs data_gml/dolphins.gml data_gml/football.gml --densities 0.40 0.60
```

Linux/macOS multiline:

```bash
graph-cluster \
  --graphs data_gml/dolphins.gml data_gml/karate.gml \
  --densities 0.40 0.60 \
  --visualize
```

Windows PowerShell multiline:

```powershell
graph-cluster `
  --graphs data_gml/dolphins.gml data_gml/karate.gml `
  --densities 0.40 0.60 `
  --visualize
```

## 8. Every CLI option

- `--graphs FILE [FILE ...]`: one or more GML dataset files.
- `--graph-folder FOLDER`: add every `.gml` and `.txt` GML file in a folder.
- `--densities VALUE [VALUE ...]`: required target densities from 0 through 1 inclusive.
- `--output FOLDER`: result root; default `results`.
- `--trace`: write `trace.txt` for each experiment.
- `--verify-with-locked`: compare optimized output against the locked reference signature and stop on mismatch.
- `--visualize`: create `cluster_visualization.png` after clustering.
- `--layout-seed INTEGER`: deterministic layout seed; default 42.
- `--hide-node-labels`: omit labels from the PNG.
- `--visualization-dpi INTEGER`: positive PNG resolution; default 300.
- `--help`: show command guidance.

## 9. Output folders and files

Each dataset-density experiment has a separate directory such as `results/dolphins/density_040/`.

### clusters.csv columns

- `cluster`: one-based cluster number.
- `nodes`: JSON-formatted node list.
- `node_count`: number of nodes.
- `recorded_internal_edge_count`: edges recorded internally during construction.
- `external_edge_count`: edges joining a cluster node to a node outside that cluster.
- `relative_density`: achieved cluster relative density.
- `difference_from_target`: absolute difference between relative and target density.

### results.json contents

Includes dataset, graph node/edge/triangle/component counts, target density, cluster number, nodes, node count, internal and external edge lists and counts, relative density, unclustered-node list, average relative density, MRDDC, recorded-edge coverage, runtime, verification state, and visualization path. The legacy key `mrddc` remains for compatibility; `mean_relative_density_deviation_coefficient` is the descriptive key.

### summary.txt

Human-readable graph statistics, clusters, cluster nodes and sizes, recorded internal-edge and external-edge counts, relative densities, average relative density, **Mean Relative Density Deviation Coefficient (MRDDC)**, recorded-edge coverage, unclustered nodes, visualization path, runtime, and verification state.

### trace.txt

Written only with `--trace`. It records algorithm execution details for inspection. Tracing does not alter cluster discovery.

### verification output

`verified_with_locked: True` means the optimized result signature matched the locked implementation for cluster order and membership, recorded internal and external edges, relative densities, and unclustered nodes.

### combined reports

`all_experiments.csv` and `all_experiments.json` summarize all experiments in the command.

## 10. Quality metrics

- **Relative density:** density achieved by one discovered cluster.
- **Average relative density:** arithmetic mean over discovered clusters.
- **Mean Relative Density Deviation Coefficient (MRDDC):** existing formula `1 - mean(|target density - cluster relative density| / target density)`. Values near 1.00 indicate close agreement with the requested density. MRDDC does not replace inspection of membership or recorded-edge coverage.
- **Recorded-edge coverage:** proportion of graph edges recorded as internal cluster edges. This differs from induced-subgraph coverage that may appear in historical notebooks.

The mathematical abbreviation URD should be interpreted as user-requested density where historical material uses it. Public commands and documentation use **target density**.

## 11. Visualization

```bash
graph-cluster --graphs data_gml/dolphins.gml --densities 0.40 --visualize
```

Each discovered cluster has a separate color; unclustered nodes are neutral gray; edges are light gray. The legend maps colors to cluster numbers. The title gives the dataset and target density. A fixed seed makes positions reproducible, but positions have no clustering meaning. Matplotlib uses the `Agg` backend, so no GUI or display is required.

## 12. Complete Dolphins worked example

Run:

```bash
graph-cluster --graphs data_gml/dolphins.gml --densities 0.40 0.60 --verify-with-locked --visualize
```

Expected folders:

```text
results/dolphins/density_040/
results/dolphins/density_060/
```

Each folder contains `clusters.csv`, `results.json`, `summary.txt`, and `cluster_visualization.png`. Both uploaded Dolphins regression densities are checked by automated tests.

## 13. Running tests

All tests:

```bash
python -m pytest
```

Visualization tests:

```bash
python -m pytest tests/test_visualization.py
```

One test:

```bash
python -m pytest tests/test_visualization.py::test_cli_visualize_creates_png
```

## 14. Troubleshooting

- **Missing graph file:** check spelling, path, and working directory.
- **Unsupported format:** provide GML content in `.gml` or `.txt`; plain edge lists are not silently converted.
- **Invalid GML:** check brackets, quotes, duplicate IDs, and edge source/target references.
- **Directed graph:** provide an undirected graph; the CLI will not convert it.
- **Weighted graph:** remove weights deliberately in a separately prepared dataset only if scientifically appropriate; the algorithm will not ignore them silently.
- **Empty graph:** add nodes and valid edges.
- **Invalid target density:** use 0 through 1 inclusive.
- **Output error:** choose an existing or creatable writable directory.
- **Missing Matplotlib/NetworkX:** activate the environment and run `python -m pip install -e .`.
- **Headless environment:** no action is required; the `Agg` backend is selected automatically.

## 15. Reproducibility

Record package version, Python and dependency versions, exact dataset file, target densities, CLI command, trace/verification settings, layout seed, and output files. Use `--verify-with-locked` for release validation. Visualization layout does not affect algorithm output.

## 16. Citation, attribution, license, and contributions

Use `CITATION.md` exactly. Preserve `ATTRIBUTION.md` and the project-specific scholarly-citation requirements in `LICENSE`. The project is not MIT licensed. Contributions must not modify locked algorithm behavior or expected signatures without an explicitly separate research-development process; see `CONTRIBUTING.md`.

## 17. GitHub release checklist

Before publishing: verify version consistency; algorithm-source hashes; dependencies; full tests; locked regression; CLI help; dataset experiments; PNG creation; README and guide commands; license, citation, and attribution; absence of caches, virtual environments, private data, local absolute paths, and debug outputs; then build and test the ZIP. See `RELEASE_CHECKLIST.md`.
