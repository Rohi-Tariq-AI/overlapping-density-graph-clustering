from pathlib import Path
import networkx as nx
from graph_clustering import PartitioningCliqueClusterer

ROOT = Path(__file__).resolve().parents[1]


def load_graph():
    return nx.read_gml(ROOT / "data" / "dolphins.gml", label="id")


def test_density_040_matches_reference_clusters():
    result = PartitioningCliqueClusterer(0.40, mode="compatible").fit(load_graph())
    expected = [
        {5, 6, 9, 13, 17, 57},
        {15, 18, 21, 24, 29, 45, 51, 59},
        {14, 16, 20, 33, 34, 37, 38, 43, 50},
        {1, 19, 25, 26, 27, 41, 54},
        {0, 2, 3, 7, 8, 10, 28, 30, 40, 42, 44, 47, 52},
    ]
    assert [set(cluster.nodes) for cluster in result.clusters] == expected
    assert [cluster.relative_density for cluster in result.clusters] == [0.40] * 5
    assert [len(cluster.internal_edges) for cluster in result.clusters] == [12, 17, 21, 10, 19]
    assert [len(cluster.external_edges) for cluster in result.clusters] == [18, 25, 32, 15, 29]


def test_density_060_still_matches_reference_clusters():
    result = PartitioningCliqueClusterer(0.60, mode="compatible").fit(load_graph())
    assert [cluster.relative_density for cluster in result.clusters] == [0.60, 0.60, 0.44]
    assert [len(cluster.internal_edges) for cluster in result.clusters] == [26, 58, 17]
    assert [len(cluster.external_edges) for cluster in result.clusters] == [17, 38, 22]
