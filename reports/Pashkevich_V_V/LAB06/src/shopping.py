import requests

class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, name, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.items.append({"name": name, "price": price})

    def total(self):
        return sum(item["price"] for item in self.items)

    def apply_discount(self, percent):
        if not 0 <= percent <= 100:
            raise ValueError("Discount must be between 0 and 100")

        current_total = self.total()
        return current_total * (1 - percent / 100)


# Функции для логирования и купонов

def log_purchase(item):
    requests.post("https://example.com/log", json=item, timeout=5)


def apply_coupon(cart, coupon_code, custom_coupons=None):
    coupons = custom_coupons if custom_coupons is not None else {"SAVE10": 10, "HALF": 50}
    if coupon_code in coupons:
        return cart.apply_discount(coupons[coupon_code])
    raise ValueError("Invalid coupon")
