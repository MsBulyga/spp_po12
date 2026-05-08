import pytest
from refactored_lab1 import sum_squares_negatives, count_climbing_ways

def test_sum_squares():
    assert sum_squares_negatives([-1, -2, 3]) == 5
    assert sum_squares_negatives([1, 2]) == 0

def test_climb_stairs():
    assert count_climbing_ways(3) == 3
    assert count_climbing_ways(4) == 5
    with pytest.raises(ValueError):
        count_climbing_ways(0)
