from copy import deepcopy
from pathlib import Path

import networkx as nx
import pytest

from graph_clustering import PartitioningCliqueClusterer
from graph_clustering.models import ClusteringResult
from graph_clustering.visualization import visualize_clusters


def test_visualization_created_and_inputs_unchanged(tmp_path):
    graph = nx.karate_club_graph()
    for _, _, data in graph.edges(data=True):
        data.clear()
    result = PartitioningCliqueClusterer(0.5, mode="compatible").fit(graph)
    graph_before = nx.node_link_data(graph)
    result_before = deepcopy(result)
    output = tmp_path / "nested" / "cluster_visualization.png"
    returned = visualize_clusters(graph, result, output, "karate.gml", 0.5)
    assert returned == output
    assert output.is_file() and output.stat().st_size > 0
    assert nx.node_link_data(graph) == graph_before
    assert result == result_before


def test_visualization_string_labels_and_all_clustered(tmp_path):
    graph = nx.complete_graph(["alpha", "beta", "gamma"])
    result = PartitioningCliqueClusterer(1.0, mode="compatible").fit(graph)
    output = tmp_path / "all.png"
    visualize_clusters(graph, result, output, "strings.gml", 1.0, layout_seed=42)
    assert output.stat().st_size > 0


def test_visualization_handles_unclustered_nodes_and_is_deterministic(tmp_path):
    graph = nx.Graph([(10, 20), (20, 30), (30, 10)])
    graph.add_node(99)
    result = PartitioningCliqueClusterer(1.0, mode="compatible").fit(graph)
    first, second = tmp_path / "first.png", tmp_path / "second.png"
    visualize_clusters(graph, result, first, "nonconsecutive.gml", 1.0, layout_seed=7)
    visualize_clusters(graph, result, second, "nonconsecutive.gml", 1.0, layout_seed=7)
    assert first.read_bytes() == second.read_bytes()


def test_visualization_handles_zero_clusters(tmp_path):
    graph = nx.path_graph(["a", "b", "c"])
    result = ClusteringResult(clusters=(), unclustered_nodes=("a", "b", "c"),
                              target_density=0.5, triangle_count=0)
    output = tmp_path / "zero.png"
    visualize_clusters(graph, result, output, "path.gml", 0.5)
    assert output.stat().st_size > 0


def test_visualization_rejects_empty_graph(tmp_path):
    result = ClusteringResult(clusters=(), unclustered_nodes=(), target_density=0.5, triangle_count=0)
    with pytest.raises(ValueError, match="empty graph"):
        visualize_clusters(nx.Graph(), result, tmp_path / "empty.png", "empty.gml", 0.5)


def test_cli_visualize_creates_png(tmp_path):
    from graph_clustering.cli import main
    dataset = Path(__file__).resolve().parents[1] / "data_gml" / "dolphins.gml"
    main(["--graphs", str(dataset), "--densities", "0.40", "--output", str(tmp_path), "--visualize"])
    png = tmp_path / "dolphins" / "density_040" / "cluster_visualization.png"
    assert png.is_file()
    assert png.stat().st_size > 0
