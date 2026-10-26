from pathlib import Path

import networkx as nx

from graph_clustering import PartitioningCliqueClusterer


def test_partitioning_clusters_are_node_disjoint():
    graph_path = Path(__file__).resolve().parents[1] / "data" / "dolphins.gml"
    graph = nx.read_gml(graph_path, label="id")
    result = PartitioningCliqueClusterer(0.60).fit(graph)

    seen = set()
    for cluster in result.clusters:
        assert seen.isdisjoint(cluster.nodes)
        seen.update(cluster.nodes)
