import pytest


def keep(s: str, pattern: str) -> str:
    if s is None and pattern is None:
        raise TypeError("Both arguments cannot be None")

    if s is None:
        return None
    if pattern is None:
        return ""
    if s == "" or pattern == "":
        return ""

    result = ""
    for char in s:
        if char in pattern:
            result += char

    return result


class TestKeep:
    def test_both_none_raises_type_error(self):
        with pytest.raises(TypeError):
            keep(None, None)

    def test_first_none_returns_none(self):
        assert keep(None, "abc") is None

    def test_first_empty_returns_empty(self):
        assert keep("", "abc") == ""

    def test_second_none_returns_empty(self):
        assert keep("abc", None) == ""

    def test_second_empty_returns_empty(self):
        assert keep("abc", "") == ""

    def test_keep_hl(self):
        assert keep(" hello ", "hl") == "hll"

    def test_keep_le(self):
        assert keep(" hello ", "le") == "ell"

    def test_keep_no_match(self):
        assert keep("abc", "xyz") == ""

    def test_keep_all_match(self):
        assert keep("aaa", "a") == "aaa"

    def test_pattern_longer_than_string(self):
        assert keep("ab", "abcd") == "ab"

    def test_keep_with_duplicates_in_pattern(self):
        result = keep("hello", "ll")
        assert result == "ll"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
