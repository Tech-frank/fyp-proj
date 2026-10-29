from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    name: str
    quantity: int = 0

    def restock(self, amount):
        self.quantity += amount
        return self.quantity
