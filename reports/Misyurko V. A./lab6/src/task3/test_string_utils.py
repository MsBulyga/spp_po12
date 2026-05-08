"""Tests for index_of_difference."""

from __future__ import annotations

import pytest

from task3.string_utils import index_of_difference


def test_index_of_difference_raises_type_error_for_two_none_values() -> None:
    """Both None values must raise TypeError."""
    with pytest.raises(TypeError):
        index_of_difference(None, None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("", "", -1),
        ("", "abc", 0),
        ("abc", "", 0),
        ("abc", "abc", -1),
        ("ab", "abxyz", 2),
        ("abcde", "abxyz", 2),
        ("abcde", "xyz", 0),
        ("i am a machine", "i am a robot", 7),
    ],
)
def test_index_of_difference_matches_specification(
    left: str, right: str, expected: int
) -> None:
    """Function should return the first differing index."""
    assert index_of_difference(left, right) == expected


def test_index_of_difference_raises_type_error_for_single_none() -> None:
    """Single None value must also raise TypeError."""
    with pytest.raises(TypeError):
        index_of_difference(None, "abc")  # type: ignore[arg-type]
