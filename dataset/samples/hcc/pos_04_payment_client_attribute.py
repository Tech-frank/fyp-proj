import requests


class PaymentClient:
    BASE_URL = "https://api.payments.example.com/v2"

    def __init__(self):
        self.session = requests.Session()
        self.api_key = "sk_live_51HqLmTzA9bXc2dEf7gHi"

    def charge(self, amount_cents, customer_id):
        return self.session.post(
            f"{self.BASE_URL}/charges",
            json={"amount": amount_cents, "customer": customer_id},
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
