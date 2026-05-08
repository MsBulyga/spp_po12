"""Mini shopping library for pytest practice."""

from __future__ import annotations

from dataclasses import dataclass

import requests

COUPONS = {"SAVE10": 10, "HALF": 50}


@dataclass(slots=True)
class Item:
    """Single cart item."""

    name: str
    price: float


class Cart:
    """Simple shopping cart."""

    def __init__(self) -> None:
        self.items: list[Item] = []

    def add_item(self, name: str, price: float) -> None:
        """Add an item to the cart."""
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.items.append(Item(name=name, price=price))

    def total(self) -> float:
        """Return the total price of all items."""
        return sum(item.price for item in self.items)

    def apply_discount(self, discount_percent: float) -> None:
        """Apply a percentage discount to every item in the cart."""
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount must be between 0 and 100")

        multiplier = (100 - discount_percent) / 100
        for item in self.items:
            item.price *= multiplier


def log_purchase(item: dict[str, object]) -> requests.Response:
    """Log a purchase to a remote system."""
    return requests.post("https://example.com/log", json=item, timeout=10)


def apply_coupon(cart: Cart, coupon_code: str) -> None:
    """Apply a predefined coupon to the cart."""
    if coupon_code in COUPONS:
        cart.apply_discount(COUPONS[coupon_code])
        return
    raise ValueError("Invalid coupon")
