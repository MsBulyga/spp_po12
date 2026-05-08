from unittest.mock import patch

import pytest
import requests


class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, name: str, price: float):
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.items.append({"name": name, "price": price})

    def total(self) -> float:
        return sum(item["price"] for item in self.items)

    def apply_discount(self, discount_percent: float):
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount must be between 0 and 100")
        for item in self.items:
            item["price"] = item["price"] * (1 - discount_percent / 100)

    def apply_coupon(self, coupon_code: str):
        coupons = {"SAVE10": 10, "HALF": 50}
        if coupon_code in coupons:
            self.apply_discount(coupons[coupon_code])
        else:
            raise ValueError("Invalid coupon")


def log_purchase(item):
    requests.post("https://example.com/log", json=item, timeout=5)


# ============ TESTS FOR TASK 1 ============


class TestCart:
    def test_add_item(self, cart):
        cart.add_item("Apple", 10.0)
        assert len(cart.items) == 1

    def test_add_item_negative_price_raises_error(self, cart):
        with pytest.raises(ValueError, match="Price cannot be negative"):
            cart.add_item("Apple", -10.0)

    def test_total(self, cart):
        cart.add_item("Apple", 10.0)
        cart.add_item("Banana", 5.0)
        assert cart.total() == 15.0

    @pytest.mark.parametrize(
        "discount,expected_price",
        [
            (0, 100.0),
            (50, 50.0),
            (100, 0.0),
        ],
    )
    def test_apply_discount(self, cart, discount, expected_price):
        cart.add_item("Item", 100.0)
        cart.apply_discount(discount)
        assert cart.items[0]["price"] == expected_price

    @pytest.mark.parametrize("invalid_discount", [-1, 101])
    def test_apply_discount_invalid_raises_error(self, cart, invalid_discount):
        cart.add_item("Item", 100.0)
        with pytest.raises(ValueError, match="Discount must be between 0 and 100"):
            cart.apply_discount(invalid_discount)


class TestLogPurchase:
    @patch("task1.requests.post")
    def test_log_purchase_calls_post_with_correct_data(self, mock_post):
        item = {"name": "Apple", "price": 10.0}
        log_purchase(item)
        mock_post.assert_called_once_with("https://example.com/log", json=item)


class TestApplyCoupon:
    @pytest.mark.parametrize(
        "coupon,discount",
        [
            ("SAVE10", 10),
            ("HALF", 50),
        ],
    )
    def test_apply_coupon_valid(self, cart, coupon, discount):
        cart.add_item("Item", 100.0)
        cart.apply_coupon(coupon)
        assert cart.items[0]["price"] == 100.0 * (1 - discount / 100)

    def test_apply_coupon_invalid_raises_error(self, cart):
        cart.add_item("Item", 100.0)
        with pytest.raises(ValueError, match="Invalid coupon"):
            cart.apply_coupon("INVALID")

    def test_apply_coupon_with_monkeypatch_coupons_dict(self, cart, monkeypatch):
        def patched_apply_coupon(self, coupon_code):
            test_coupons = {"TEST": 25}
            if coupon_code in test_coupons:
                self.apply_discount(test_coupons[coupon_code])
            else:
                raise ValueError("Invalid coupon")

        monkeypatch.setattr(Cart, "apply_coupon", patched_apply_coupon)
        cart.add_item("Item", 100.0)
        cart.apply_coupon("TEST")
        assert cart.items[0]["price"] == 75.0


@pytest.fixture
def cart():
    return Cart()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
