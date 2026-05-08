from unittest.mock import patch
import pytest
from shopping import Cart, apply_coupon
from shopping import log_purchase
# pylint: disable=redefined-outer-name

@pytest.fixture
def empty_cart():
    return Cart()

def test_add_item(empty_cart):
    empty_cart.add_item("Apple", 10.0)
    assert len(empty_cart.items) == 1

def test_negative_price(empty_cart):
    with pytest.raises(ValueError):
        empty_cart.add_item("Apple", -1.0)

def test_total(empty_cart):
    empty_cart.add_item("Apple", 10.0)
    empty_cart.add_item("Banana", 5.0)
    assert empty_cart.total() == 15.0

@pytest.mark.parametrize("discount, expected", [
    (0, 100),
    (50, 50),
    (100, 0),
])
def test_apply_discount(empty_cart, discount, expected):
    empty_cart.add_item("Item", 100)
    assert empty_cart.apply_discount(discount) == expected

@pytest.mark.parametrize("invalid_discount", [-10, 110])
def test_apply_discount_error(empty_cart, invalid_discount):
    with pytest.raises(ValueError):
        empty_cart.apply_discount(invalid_discount)

# Тест логирования с моком
def test_log_purchase():
    with patch('requests.post') as mocked_post:
        # Импорт уже должен быть вверху файла
        item = {"name": "Apple", "price": 10.0}
        log_purchase(item)

        # Добавляем аргумент timeout=5 в ожидаемый вызов
        mocked_post.assert_called_once_with(
            "https://example.com/log",
            json=item,
            timeout=5
        )

# Тест купонов с patch.dict
def test_apply_coupon(empty_cart):
    empty_cart.add_item("Item", 100)
    # Передаем словарь прямо в функцию
    my_coupons = {"TEST": 20}
    assert apply_coupon(empty_cart, "TEST", custom_coupons=my_coupons) == 80
