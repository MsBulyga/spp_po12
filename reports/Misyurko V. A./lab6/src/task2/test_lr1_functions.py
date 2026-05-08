"""Tests for refactored functions from laboratory work 1."""

from __future__ import annotations

import pytest

from task2.lr1_functions import count_climbing_ways, sort_numbers_desc


@pytest.mark.parametrize(
    ("numbers", "expected"),
    [
        ([3, 1, 2], [3, 2, 1]),
        ([], []),
        ([5], [5]),
        ([4, 4, 2], [4, 4, 2]),
        ([-1, 7, 0, -3], [7, 0, -1, -3]),
    ],
)
def test_sort_numbers_desc_returns_numbers_in_descending_order(
    numbers: list[int], expected: list[int]
) -> None:
    """Sorting should return values in descending order."""
    assert sort_numbers_desc(numbers) == expected


def test_sort_numbers_desc_does_not_modify_original_list() -> None:
    """Function should return a new sorted list."""
    numbers = [2, 1, 3]

    result = sort_numbers_desc(numbers)

    assert result == [3, 2, 1]
    assert numbers == [2, 1, 3]


@pytest.mark.parametrize(
    ("steps", "expected"),
    [
        (0, 1),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 5),
        (5, 8),
        (10, 89),
    ],
)
def test_count_climbing_ways_returns_expected_values(
    steps: int, expected: int
) -> None:
    """Function should match the known climbing stairs sequence."""
    assert count_climbing_ways(steps) == expected


def test_count_climbing_ways_raises_for_negative_value() -> None:
    """Negative steps must raise ValueError."""
    with pytest.raises(ValueError, match="Number of steps cannot be negative"):
        count_climbing_ways(-1)
