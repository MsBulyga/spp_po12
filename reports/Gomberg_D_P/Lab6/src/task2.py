import os
import sys

import pytest

from Test1 import find_mode
from Test2 import str_str

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Lab1", "src"))


class TestFindMode:
    def test_empty_sequence_returns_none(self):
        assert find_mode([]) is None

    def test_no_mode_all_elements_same_frequency(self):
        assert find_mode([1, 2, 3]) is None

    def test_single_mode(self):
        assert find_mode([1, 2, 2, 3]) == [2]

    def test_multiple_modes(self):
        result = find_mode([1, 1, 2, 2, 3])
        assert set(result) == {1, 2}

    def test_single_element(self):
        assert find_mode([5]) is None

    def test_all_same_elements(self):
        assert find_mode([7, 7, 7]) is None

    def test_negative_numbers(self):
        result = find_mode([-1, -1, -2, -2, -3])
        assert set(result) == {-1, -2}

    def test_strings(self):
        result = find_mode(["a", "b", "a", "c", "b"])
        assert set(result) == {"a", "b"}


class TestStrStr:
    def test_empty_haystack_returns_negative(self):
        assert str_str("", "abc") == -1

    def test_empty_needle_returns_zero(self):
        assert str_str("abc", "") == 0

    def test_both_empty_returns_zero(self):
        assert str_str("", "") == 0

    def test_needle_not_found(self):
        assert str_str("hello", "world") == -1

    def test_needle_found_at_beginning(self):
        assert str_str("hello", "he") == 0

    def test_needle_found_at_end(self):
        assert str_str("hello", "lo") == 3

    def test_needle_found_in_middle(self):
        assert str_str("ffsadbutsad", "sad") == 2

    def test_needle_longer_than_haystack(self):
        assert str_str("abc", "abcd") == -1

    def test_exact_match(self):
        assert str_str("abc", "abc") == 0

    def test_overlapping_needle(self):
        assert str_str("aaa", "aa") == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
