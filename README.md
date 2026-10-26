# Overlapping Graph Clustering with User-Specified Density

A triangle-seeded graph clustering implementation that returns overlapping clusters near a user-specified relative density.

## Method

For the same graph, node order, triangle order, target density, and tie-breaking rules, the first cluster is identical to the partitioning method.

For every later cluster:

1. The starting triangle contains no node from any earlier accepted cluster.
2. The starting triangle is selected by the average adjusted triangle-degree rule.
3. After initialization, expansion uses the complete graph.
4. Nodes from earlier clusters may enter during expansion, creating overlap.

Relative density is

```text
internal edges / (internal edges + external edges)
```

Conductance is not used.

## Installation

```bash
git clone https://github.com/Rohi-Tariq-AI/overlapping-density-graph-clustering.git
cd overlapping-density-graph-clustering
python -m pip install -e .
```

## Command-line use

```bash
overlap-cluster \
  data_gml/karate.gml \
  --density 0.40 \
  --mode corrected \
  --output results/karate_040
```

The command creates:

```text
results.json
clusters.csv
summary.txt
```

The summary includes total nodes and edges, triangle count, number of clusters, clustered node count, overlapping node count, unclustered node count, average relative density, MRDDC, and edge-coverage measures.

## Python API

```python
import networkx as nx
from graph_clustering import OverlappingCliqueClusterer

graph = nx.read_gml("data_gml/karate.gml", label="id")
graph = nx.Graph(graph)
graph.remove_edges_from(nx.selfloop_edges(graph))

result = OverlappingCliqueClusterer(
    target_density=0.40,
    mode="corrected",
).fit(graph)

for number, cluster in enumerate(result.clusters, start=1):
    print(number, cluster.starting_triangle, cluster.nodes, cluster.relative_density)

print("Overlapping nodes:", result.overlapping_nodes)
print("Unclustered nodes:", result.unclustered_nodes)
```

## Included datasets

- Karate Club
- Dolphins
- American college football
- Political books
- Les Miserables
- Power Grid
- Facebook
- Weaver bird social network

## Tests

```bash
python -m pytest -q
```

## Repository structure

```text
src/graph_clustering/   implementation
tests/                  automated tests
examples/               runnable example
data_gml/               GML datasets
data_edge_lists/        edge-list datasets
```

## Citation and license

See `CITATION.md`, `ATTRIBUTION.md`, and `LICENSE`.
