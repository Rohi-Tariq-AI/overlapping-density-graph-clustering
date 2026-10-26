import networkx as nx

from graph_clustering import OverlappingCliqueClusterer

# NetworkX's built-in Karate graph includes weight attributes. The published
# method works on an unweighted graph, so copy only the edge endpoints.
graph = nx.Graph(nx.karate_club_graph().edges())
result = OverlappingCliqueClusterer(0.40, mode="compatible").fit(graph)

for number, cluster in enumerate(result.clusters, start=1):
    print(f"Cluster {number}")
    print("  start:", cluster.starting_triangle)
    print("  nodes:", cluster.nodes)
    print("  relative density:", cluster.relative_density)

print("Overlapping nodes:", result.overlapping_nodes)
print("Unclustered nodes:", result.unclustered_nodes)
