import pytest
from zadanie3 import keep

def test_keep_basic():
    # Чтобы получить " hll ", нужно разрешить и 'h', и 'l', и ' ' (пробел)
    assert keep(" hello ", "hl ") == " hll "

def test_keep_empty():
    assert keep("", "abc") == ""
    assert keep("abc", "") == ""

def test_keep_type_error():
    with pytest.raises(TypeError):
        keep(None, "abc")
    with pytest.raises(TypeError):
        keep("abc", None)
