from pathlib import Path

import networkx as nx

from graph_clustering.triangles import find_triangles


def test_dolphins_graph_reference_counts():
    graph_path = Path(__file__).resolve().parents[1] / "data" / "dolphins.gml"
    graph = nx.read_gml(graph_path, label="id")
    assert graph.number_of_nodes() == 62
    assert graph.number_of_edges() == 159
    assert len(find_triangles(graph, mode="compatible")) == 95
