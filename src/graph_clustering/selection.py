from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")


def select_average_candidate(
    candidates: Sequence[T],
    degree: Callable[[T], int],
    mode: str = "compatible",
) -> tuple[T, int, list[int], int]:
    """Return candidate, original index, degrees, and truncated average."""
    if not candidates:
        raise ValueError("At least one candidate is required.")
    degrees = [degree(candidate) for candidate in candidates]
    average = int(sum(degrees) / len(degrees))

    if mode == "corrected":
        index = min(range(len(candidates)), key=lambda i: abs(degrees[i] - average))
        return candidates[index], index, degrees, average
    if mode != "compatible":
        raise ValueError("mode must be 'compatible' or 'corrected'")

    if average in degrees:
        index = degrees.index(average)
        return candidates[index], index, degrees, average

    ordered = sorted(degrees)
    selected_degree = ordered[0]
    for i, value in enumerate(ordered):
        if value > average:
            lower = ordered[i - 1]
            upper = value
            selected_degree = upper if abs(lower-average) >= abs(upper-average) else lower
            break
    index = degrees.index(selected_degree)
    return candidates[index], index, degrees, average


def first_closest_to_integer_average(candidates, degree):
    return select_average_candidate(candidates, degree, mode="corrected")[0]
