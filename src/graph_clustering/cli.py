import argparse
import csv
import json
import time
from pathlib import Path

import networkx as nx

from .optimized import OptimizedPartitioningCliqueClusterer, ScalablePartitioningCliqueClusterer
from .partitioning import PartitioningCliqueClusterer
from .quality import (
    average_relative_density,
    mean_relative_density_deviation_coefficient,
    recorded_edge_coverage,
)


def _unique(items):
    out = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def _slug(density):
    return f"density_{int(round(density * 100)):03d}"


def _load(path):
    if path.suffix.lower() not in {".gml", ".txt"}:
        raise ValueError(f"Unsupported dataset format for '{path}'. Use a GML file (.gml or .txt).")
    try:
        try:
            graph = nx.read_gml(path, label="id")
        except Exception:
            graph = nx.read_gml(path)
    except Exception as exc:
        raise ValueError(f"Could not load GML dataset '{path}': {exc}") from exc
    if graph.number_of_nodes() == 0:
        raise ValueError(f"Dataset '{path}' contains an empty graph.")
    return graph


def _signature(result):
    return (
        [tuple(c.nodes) for c in result.clusters],
        [set(map(frozenset, c.internal_edges)) for c in result.clusters],
        [set(map(frozenset, c.external_edges)) for c in result.clusters],
        [c.relative_density for c in result.clusters],
        tuple(result.unclustered_nodes),
    )


def run_experiment(path, density, outroot, trace=False, verify=False, visualize=False,
                   layout_seed=42, show_labels=True, visualization_dpi=300):
    graph = _load(path)
    if graph.is_directed():
        raise ValueError(f"{path}: only undirected graphs are supported")
    folder = outroot / path.stem / _slug(density)
    folder.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    engine = OptimizedPartitioningCliqueClusterer(density, mode="compatible", trace=trace)
    result = engine.fit(graph)
    elapsed = time.perf_counter() - start

    verified = None
    if verify:
        locked = PartitioningCliqueClusterer(density, mode="compatible").fit(graph)
        verified = _signature(locked) == _signature(result)
        if not verified:
            raise RuntimeError(f"Locked/scalable mismatch: {path}, {density}")

    visualization_path = None
    if visualize:
        from .visualization import visualize_clusters
        visualization_path = visualize_clusters(
            graph, result, folder / "cluster_visualization.png", path.name, density,
            layout_seed=layout_seed, show_labels=show_labels, dpi=visualization_dpi,
        )

    cluster_rows = []
    for index, cluster in enumerate(result.clusters, 1):
        cluster_rows.append({
            "cluster": index,
            "nodes": json.dumps(list(cluster.nodes)),
            "node_count": len(cluster.nodes),
            "recorded_internal_edge_count": len(cluster.internal_edges),
            "external_edge_count": len(cluster.external_edges),
            "relative_density": cluster.relative_density,
            "difference_from_target": round(abs(cluster.relative_density - density), 2),
        })
    with (folder / "clusters.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = cluster_rows[0].keys() if cluster_rows else ["cluster"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(cluster_rows)

    average = average_relative_density(result.clusters)
    coefficient = mean_relative_density_deviation_coefficient(density, result.clusters)
    coverage = recorded_edge_coverage(graph, result.clusters)
    details = {
        "dataset": path.name,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "triangles": sum(nx.triangles(graph).values()) // 3,
        "components": nx.number_connected_components(graph),
        "target_density": density,
        "clusters": [{
            "number": index,
            "nodes": list(cluster.nodes),
            "internal_edges": [list(edge) for edge in cluster.internal_edges],
            "external_edges": [list(edge) for edge in cluster.external_edges],
            "relative_density": cluster.relative_density,
            "node_count": len(cluster.nodes),
            "recorded_internal_edge_count": len(cluster.internal_edges),
            "external_edge_count": len(cluster.external_edges),
        } for index, cluster in enumerate(result.clusters, 1)],
        "unclustered_nodes": list(result.unclustered_nodes),
        "average_relative_density": average,
        "mrddc": coefficient,
        "mean_relative_density_deviation_coefficient": coefficient,
        "recorded_edge_coverage": coverage,
        "runtime_seconds": round(elapsed, 6),
        "verified_with_locked": verified,
        "visualization_path": str(visualization_path) if visualization_path else None,
    }
    (folder / "results.json").write_text(json.dumps(details, indent=2), encoding="utf-8")
    summary = "\n".join([
        f"Dataset: {path.name}",
        f"Nodes: {graph.number_of_nodes()}",
        f"Edges: {graph.number_of_edges()}",
        f"Triangles: {details['triangles']}",
        f"Target density: {density:.2f}",
        f"Clusters: {len(result.clusters)}",
        f"Cluster nodes: {[list(c.nodes) for c in result.clusters]}",
        f"Cluster sizes: {[len(c.nodes) for c in result.clusters]}",
        f"Recorded internal-edge counts: {[len(c.internal_edges) for c in result.clusters]}",
        f"External-edge counts: {[len(c.external_edges) for c in result.clusters]}",
        f"Relative densities: {[c.relative_density for c in result.clusters]}",
        f"Average relative density: {average:.2f}",
        f"Mean Relative Density Deviation Coefficient (MRDDC): {coefficient:.2f}",
        f"Recorded-edge coverage: {coverage:.2f}",
        f"Unclustered nodes ({len(result.unclustered_nodes)}): {list(result.unclustered_nodes)}",
        f"Visualization: {visualization_path if visualization_path else 'Not requested'}",
        f"Runtime seconds: {elapsed:.6f}",
        f"Verified with locked: {verified}",
    ])
    (folder / "summary.txt").write_text(summary + "\n", encoding="utf-8")
    if trace:
        engine.write_trace(str(folder / "trace.txt"))
    return {
        "dataset": path.name,
        "target_density": density,
        "clusters": len(result.clusters),
        "cluster_sizes": json.dumps([len(c.nodes) for c in result.clusters]),
        "relative_densities": json.dumps([c.relative_density for c in result.clusters]),
        "average_relative_density": average,
        "mrddc": coefficient,
        "mean_relative_density_deviation_coefficient": coefficient,
        "recorded_edge_coverage": coverage,
        "unclustered_nodes": len(result.unclustered_nodes),
        "runtime_seconds": round(elapsed, 6),
        "verified_with_locked": verified,
        "visualization_path": str(visualization_path) if visualization_path else None,
        "result_folder": str(folder),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Discover clusters in undirected GML graphs at user-selected target densities."
    )
    parser.add_argument("--graphs", nargs="+", type=Path, help="One or more GML dataset files.")
    parser.add_argument("--graph-folder", type=Path, help="Folder containing .gml or .txt GML datasets.")
    parser.add_argument("--densities", nargs="+", type=float, required=True,
                        help="One or more target densities from 0 through 1.")
    parser.add_argument("--output", type=Path, default=Path("results"),
                        help="Output directory (default: results).")
    parser.add_argument("--trace", action="store_true", help="Write algorithm trace.txt output.")
    parser.add_argument("--verify-with-locked", action="store_true",
                        help="Compare optimized results with the locked reference implementation.")
    parser.add_argument("--visualize", action="store_true",
                        help="Save cluster_visualization.png after each clustering experiment.")
    parser.add_argument("--layout-seed", type=int, default=42,
                        help="Deterministic visualization layout seed (default: 42).")
    parser.add_argument("--hide-node-labels", action="store_true",
                        help="Hide node labels in visualization images.")
    parser.add_argument("--visualization-dpi", type=int, default=300,
                        help="Visualization PNG resolution (default: 300 DPI).")
    args = parser.parse_args(argv)

    graphs = list(args.graphs or [])
    if args.graph_folder:
        if not args.graph_folder.is_dir():
            parser.error(f"Graph folder does not exist or is not a directory: {args.graph_folder}")
        graphs += sorted(args.graph_folder.glob("*.txt")) + sorted(args.graph_folder.glob("*.gml"))
    graphs = _unique([item.resolve() for item in graphs])
    densities = _unique(args.densities)
    if not graphs:
        parser.error("Provide --graphs and/or --graph-folder.")
    missing = [str(path) for path in graphs if not path.is_file()]
    if missing:
        parser.error("Dataset file not found: " + ", ".join(missing))
    if any(not 0 <= density <= 1 for density in densities):
        parser.error("Target densities must be between 0 and 1 inclusive.")
    if args.visualization_dpi <= 0:
        parser.error("--visualization-dpi must be a positive integer.")

    try:
        args.output.mkdir(parents=True, exist_ok=True)
        if not args.output.is_dir():
            parser.error(f"Output path is not a directory: {args.output}")
        probe = args.output / ".graph_clustering_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        parser.error(f"Output directory is not writable: {args.output}: {exc}")

    rows = []
    print(f"Datasets: {len(graphs)} | Densities: {len(densities)} | Experiments: {len(graphs) * len(densities)}")
    for graph_path in graphs:
        for density in densities:
            row = run_experiment(
                graph_path, density, args.output, args.trace, args.verify_with_locked,
                args.visualize, args.layout_seed, not args.hide_node_labels, args.visualization_dpi,
            )
            rows.append(row)
            print(f"{graph_path.name} @ {density:.2f}: {row['clusters']} clusters, {row['runtime_seconds']:.4f}s")

    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "all_experiments.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    (args.output / "all_experiments.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Combined report: {args.output / 'all_experiments.csv'}")


if __name__ == "__main__":
    main()
