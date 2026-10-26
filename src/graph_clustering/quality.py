"""Published quality metrics for user-specified-density clustering."""
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(value: float, digits: int = 2) -> float:
    quantum = Decimal("1").scaleb(-digits)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))

def recorded_edge_coverage(graph, clusters) -> float:
    if graph.number_of_edges() == 0:
        return 0.0
    return round_half_up(sum(len(c.internal_edges) for c in clusters) / graph.number_of_edges())

def average_relative_density(clusters) -> float:
    if not clusters:
        return 0.0
    return round_half_up(sum(c.relative_density for c in clusters) / len(clusters))

def mean_relative_density_deviation_coefficient(target_density: float, clusters) -> float:
    """MRDDC: agreement of returned relative densities with the requested value."""
    if not clusters:
        return 0.0
    if target_density == 0:
        return 1.0 if all(c.relative_density == 0 for c in clusters) else 0.0
    mean_relative_deviation = sum(
        abs(target_density - c.relative_density) / target_density for c in clusters
    ) / len(clusters)
    return round_half_up(1.0 - mean_relative_deviation)

# Backward-compatible aliases.
coverage = recorded_edge_coverage
agreement_coefficient = mean_relative_density_deviation_coefficient
