"""Refactored functions from laboratory work 1."""

from __future__ import annotations


def sort_numbers_desc(numbers: list[int]) -> list[int]:
    """Return numbers sorted in descending order."""
    return sorted(numbers, reverse=True)


def count_climbing_ways(steps: int) -> int:
    """Return the number of ways to reach the top using 1 or 2 steps."""
    if steps < 0:
        raise ValueError("Number of steps cannot be negative")
    if steps in {0, 1}:
        return 1

    previous = 1
    current = 1
    for _ in range(2, steps + 1):
        previous, current = current, previous + current
    return current
