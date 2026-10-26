"""Post-processing visualization for completed clustering results.

This module does not participate in cluster discovery or metric calculation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx


def visualize_clusters(
    graph: nx.Graph,
    clustering_result: Any,
    output_path: str | Path,
    dataset_name: str,
    target_density: float,
    layout_seed: int = 42,
    show_labels: bool = True,
    dpi: int = 300,
) -> Path:
    """Save a PNG showing discovered clusters without modifying inputs."""
    if not isinstance(graph, nx.Graph):
        raise TypeError("Visualization requires a NetworkX graph.")
    if graph.is_directed():
        raise ValueError("Visualization supports undirected graphs only.")
    if graph.number_of_nodes() == 0:
        raise ValueError("Visualization cannot be generated for an empty graph.")
    if dpi <= 0:
        raise ValueError("Visualization DPI must be a positive integer.")
    if not hasattr(clustering_result, "clusters") or not hasattr(clustering_result, "unclustered_nodes"):
        raise TypeError("Invalid clustering result: expected clusters and unclustered_nodes.")

    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        position = nx.spring_layout(graph, seed=layout_seed)
        cluster_count = max(1, len(clustering_result.clusters))
        palette = plt.get_cmap("hsv", cluster_count + 1)
        node_colors: dict[Any, Any] = {}
        legend: list[Line2D] = []
        for index, cluster in enumerate(clustering_result.clusters, start=1):
            color = palette(index - 1)
            for node in cluster.nodes:
                if node in graph:
                    node_colors[node] = color
            legend.append(Line2D([0], [0], marker="o", color="w", label=f"Cluster {index}",
                                 markerfacecolor=color, markersize=8))

        unclustered = set(clustering_result.unclustered_nodes)
        neutral = "#9e9e9e"
        colors = [node_colors.get(node, neutral) for node in graph.nodes]
        if unclustered or any(node not in node_colors for node in graph.nodes):
            legend.append(Line2D([0], [0], marker="o", color="w", label="Unclustered nodes",
                                 markerfacecolor=neutral, markersize=8))

        figure_size = max(7.0, min(14.0, 6.0 + graph.number_of_nodes() / 15.0))
        fig, ax = plt.subplots(figsize=(figure_size, figure_size * 0.75))
        try:
            nx.draw_networkx_edges(graph, position, ax=ax, edge_color="#d0d0d0", width=0.8, alpha=0.75)
            nx.draw_networkx_nodes(graph, position, ax=ax, node_color=colors, node_size=320,
                                   edgecolors="white", linewidths=0.6)
            if show_labels:
                nx.draw_networkx_labels(graph, position, ax=ax, font_size=7)
            ax.set_title(f"{dataset_name} | Target density: {target_density:.2f}")
            ax.set_axis_off()
            if legend:
                ax.legend(handles=legend, loc="best", frameon=True, fontsize=8)
            fig.tight_layout()
            fig.savefig(path, format="png", dpi=dpi, bbox_inches="tight")
        finally:
            plt.close(fig)
    except (OSError, ValueError, TypeError) as exc:
        if isinstance(exc, (ValueError, TypeError)) and str(exc).startswith("Visualization"):
            raise
        raise RuntimeError(f"Visualization could not be generated at '{path}': {exc}") from exc
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Visualization could not be generated at '{path}'.")
    return path
