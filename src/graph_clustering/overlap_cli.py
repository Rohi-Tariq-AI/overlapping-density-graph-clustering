from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import networkx as nx

from .overlapping import OverlappingCliqueClusterer
from .quality import (
    average_relative_density,
    mean_relative_density_deviation_coefficient,
)


def load_graph(path: Path) -> nx.Graph:
    """Load a GML file or an undirected edge-list file."""
    if path.suffix.lower() == ".gml":
        try:
            graph = nx.read_gml(path, label="id")
        except Exception:
            graph = nx.read_gml(path)
    else:
        try:
            graph = nx.read_edgelist(
                path,
                nodetype=int,
                create_using=nx.Graph(),
            )
        except Exception:
            graph = nx.read_edgelist(
                path,
                create_using=nx.Graph(),
            )

    graph = nx.Graph(graph)
    graph.remove_edges_from(nx.selfloop_edges(graph))
    return graph


def serializable(
    result,
    graph: nx.Graph,
    source: str,
) -> dict:
    """Convert a clustering result into JSON-compatible data."""
    unique_edges = set()
    weighted_internal_edge_count = 0
    clusters = []
    memberships = {
        str(node): []
        for node in graph.nodes()
    }

    for number, cluster in enumerate(
        result.clusters,
        start=1,
    ):
        weighted_internal_edge_count += len(
            cluster.internal_edges
        )

        unique_edges.update(
            frozenset(edge)
            for edge in cluster.internal_edges
        )

        for node in cluster.nodes:
            memberships[str(node)].append(number)

        clusters.append(
            {
                "cluster": number,
                "starting_triangle": list(
                    cluster.starting_triangle
                ),
                "nodes": list(cluster.nodes),
                "internal_edges": [
                    list(edge)
                    for edge in cluster.internal_edges
                ],
                "external_edges": [
                    list(edge)
                    for edge in cluster.external_edges
                ],
                "relative_density": (
                    cluster.relative_density
                ),
                "used_triangles": [
                    list(triangle)
                    for triangle in cluster.used_triangles
                ],
            }
        )

    edge_count = graph.number_of_edges()

    unique_edge_coverage = (
        round(len(unique_edges) / edge_count, 4)
        if edge_count
        else 0.0
    )

    membership_weighted_edge_coverage = (
        round(
            weighted_internal_edge_count / edge_count,
            4,
        )
        if edge_count
        else 0.0
    )

    return {
        "source": source,
        "target_density": result.target_density,
        "nodes": graph.number_of_nodes(),
        "edges": edge_count,
        "triangle_count": result.triangle_count,
        "cluster_count": len(result.clusters),
        "clusters": clusters,
        "overlapping_nodes": list(
            result.overlapping_nodes
        ),
        "overlapping_memberships": {
            node: cluster_numbers
            for node, cluster_numbers in memberships.items()
            if len(cluster_numbers) > 1
        },
        "unclustered_nodes": list(
            result.unclustered_nodes
        ),
        "average_relative_density": (
            average_relative_density(result.clusters)
        ),
        "mrddc": (
            mean_relative_density_deviation_coefficient(
                result.target_density,
                result.clusters,
            )
        ),
        "unique_edge_coverage": unique_edge_coverage,
        "membership_weighted_edge_coverage": (
            membership_weighted_edge_coverage
        ),
    }


def write_outputs(
    payload: dict,
    output: Path,
) -> None:
    """Write JSON, CSV, and human-readable summary outputs."""
    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    (output / "results.json").write_text(
        json.dumps(
            payload,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    with (output / "clusters.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "cluster",
                "starting_triangle",
                "nodes",
                "internal_edges",
                "external_edges",
                "relative_density",
            ]
        )

        for cluster in payload["clusters"]:
            writer.writerow(
                [
                    cluster["cluster"],
                    json.dumps(
                        cluster["starting_triangle"]
                    ),
                    json.dumps(cluster["nodes"]),
                    len(cluster["internal_edges"]),
                    len(cluster["external_edges"]),
                    cluster["relative_density"],
                ]
            )

    clustered_node_count = (
        payload["nodes"]
        - len(payload["unclustered_nodes"])
    )

    overlapping_node_count = len(
        payload["overlapping_nodes"]
    )

    unclustered_node_count = len(
        payload["unclustered_nodes"]
    )

    lines = [
        f"Source: {payload['source']}",
        (
            "Target density: "
            f"{payload['target_density']:.2f}"
        ),
        f"Total graph nodes: {payload['nodes']}",
        f"Total graph edges: {payload['edges']}",
        f"Total triangles: {payload['triangle_count']}",
        f"Number of clusters: {payload['cluster_count']}",
        f"Clustered node count: {clustered_node_count}",
        f"Overlapping node count: {overlapping_node_count}",
        f"Unclustered node count: {unclustered_node_count}",
        (
            "Average relative density: "
            f"{payload['average_relative_density']:.2f}"
        ),
        f"MRDDC: {payload['mrddc']:.2f}",
        (
            "Unique edge coverage: "
            f"{payload['unique_edge_coverage']:.4f}"
        ),
        (
            "Membership-weighted edge coverage: "
            f"{payload['membership_weighted_edge_coverage']:.4f}"
        ),
        "",
        (
            "Overlapping nodes: "
            f"{payload['overlapping_nodes']}"
        ),
        (
            "Unclustered nodes: "
            f"{payload['unclustered_nodes']}"
        ),
    ]

    (output / "summary.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main(argv=None) -> int:
    """Run overlapping graph clustering from the command line."""
    parser = argparse.ArgumentParser(
        description=(
            "Clique-based overlapping graph clustering "
            "with user-specified density"
        )
    )

    parser.add_argument(
        "graph",
        type=Path,
        help="Path to a GML or edge-list graph file.",
    )

    parser.add_argument(
        "--density",
        type=float,
        required=True,
        help="Requested relative density between 0 and 1.",
    )

    parser.add_argument(
        "--mode",
        choices=["compatible", "corrected"],
        default="compatible",
        help="Triangle enumeration and selection mode.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("overlapping_results"),
        help="Directory for JSON, CSV, and text outputs.",
    )

    arguments = parser.parse_args(argv)

    graph = load_graph(arguments.graph)

    result = OverlappingCliqueClusterer(
        arguments.density,
        mode=arguments.mode,
    ).fit(graph)

    payload = serializable(
        result,
        graph,
        str(arguments.graph),
    )

    write_outputs(
        payload,
        arguments.output,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
