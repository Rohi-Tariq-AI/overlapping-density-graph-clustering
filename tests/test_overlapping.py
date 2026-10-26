import networkx as nx

from graph_clustering import OverlappingCliqueClusterer, PartitioningCliqueClusterer


def test_karate_first_cluster_matches_partitioning():
    graph = nx.Graph(nx.karate_club_graph().edges())
    partitioning = PartitioningCliqueClusterer(0.40, mode="compatible").fit(graph)
    overlapping = OverlappingCliqueClusterer(0.40, mode="compatible").fit(graph)

    p = partitioning.clusters[0]
    o = overlapping.clusters[0]
    assert o.starting_triangle == (0, 3, 7)
    assert set(p.nodes) == set(o.nodes)
    assert set(p.internal_edges) == set(o.internal_edges)
    assert set(p.external_edges) == set(o.external_edges)
    assert p.relative_density == o.relative_density == 0.42


def test_each_later_start_is_disjoint_from_earlier_clusters():
    result = OverlappingCliqueClusterer(0.40, mode="compatible").fit(
        nx.Graph(nx.karate_club_graph().edges())
    )
    earlier_nodes = set()
    for cluster in result.clusters:
        assert set(cluster.starting_triangle).isdisjoint(earlier_nodes)
        earlier_nodes.update(cluster.nodes)


def test_overlap_is_allowed_after_disjoint_initialization():
    result = OverlappingCliqueClusterer(0.40, mode="compatible").fit(
        nx.Graph(nx.karate_club_graph().edges())
    )
    assert result.overlapping_nodes


def test_density_is_consistent_for_every_cluster():
    result = OverlappingCliqueClusterer(0.40, mode="compatible").fit(
        nx.Graph(nx.karate_club_graph().edges())
    )
    for cluster in result.clusters:
        denominator = len(cluster.internal_edges) + len(cluster.external_edges)
        assert round(len(cluster.internal_edges) / denominator, 2) == cluster.relative_density


def test_input_graph_is_not_modified():
    graph = nx.Graph(nx.karate_club_graph().edges())
    original_nodes = set(graph.nodes())
    original_edges = {frozenset(edge) for edge in graph.edges()}
    OverlappingCliqueClusterer(0.40, mode="compatible").fit(graph)
    assert set(graph.nodes()) == original_nodes
    assert {frozenset(edge) for edge in graph.edges()} == original_edges
