"""String utility functions for task 3."""

from __future__ import annotations


def index_of_difference(str1: str, str2: str) -> int:
    """Return the first index where two strings differ."""
    if str1 is None and str2 is None:
        raise TypeError("Both strings cannot be None")
    if str1 is None or str2 is None:
        raise TypeError("String arguments cannot be None")

    if str1 == str2:
        return -1

    limit = min(len(str1), len(str2))
    for index in range(limit):
        if str1[index] != str2[index]:
            return index

    return limit
