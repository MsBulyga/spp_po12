"""Tests for the mini shopping library."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from task1.shopping import Cart, apply_coupon, log_purchase


@pytest.fixture
def empty_cart() -> Cart:
    """Return a fresh empty cart."""
    return Cart()


def test_add_item_adds_one_item_to_cart(empty_cart: Cart) -> None:
    """Item should be added to the cart."""
    empty_cart.add_item("Apple", 10.0)

    assert len(empty_cart.items) == 1
    assert empty_cart.items[0].name == "Apple"
    assert empty_cart.items[0].price == 10.0


def test_add_item_raises_error_for_negative_price(empty_cart: Cart) -> None:
    """Negative prices must raise ValueError."""
    with pytest.raises(ValueError, match="Price cannot be negative"):
        empty_cart.add_item("Apple", -10.0)


def test_total_returns_sum_of_item_prices(empty_cart: Cart) -> None:
    """Total should equal the sum of all items."""
    empty_cart.add_item("Apple", 10.0)
    empty_cart.add_item("Banana", 5.5)

    assert empty_cart.total() == pytest.approx(15.5)


@pytest.mark.parametrize(
    ("discount_percent", "expected_total"),
    [
        (0, 20.0),
        (50, 10.0),
        (100, 0.0),
    ],
)
def test_apply_discount_valid_values(
    empty_cart: Cart, discount_percent: float, expected_total: float
) -> None:
    """Valid discounts should update the total correctly."""
    empty_cart.add_item("Apple", 20.0)

    empty_cart.apply_discount(discount_percent)

    assert empty_cart.total() == pytest.approx(expected_total)


@pytest.mark.parametrize("discount_percent", [-1, 101])
def test_apply_discount_invalid_values_raise_error(
    empty_cart: Cart, discount_percent: float
) -> None:
    """Discount outside 0..100 must raise ValueError."""
    empty_cart.add_item("Apple", 20.0)

    with pytest.raises(ValueError, match="Discount must be between 0 and 100"):
        empty_cart.apply_discount(discount_percent)


def test_log_purchase_calls_requests_post_with_correct_data() -> None:
    """Remote logging should call requests.post with expected arguments."""
    item = {"name": "Apple", "price": 10.0}

    with patch("task1.shopping.requests.post") as mocked_post:
        log_purchase(item)

    mocked_post.assert_called_once_with(
        "https://example.com/log",
        json=item,
        timeout=10,
    )


def test_apply_coupon_uses_mocked_coupon_dictionary(
    empty_cart: Cart, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Coupon discount should be taken from the patched coupon map."""
    empty_cart.add_item("Apple", 100.0)
    monkeypatch.setattr("task1.shopping.COUPONS", {"TEST25": 25})

    apply_coupon(empty_cart, "TEST25")

    assert empty_cart.total() == pytest.approx(75.0)


def test_apply_coupon_raises_error_for_invalid_coupon(empty_cart: Cart) -> None:
    """Unknown coupon must raise ValueError."""
    with pytest.raises(ValueError, match="Invalid coupon"):
        apply_coupon(empty_cart, "UNKNOWN")
