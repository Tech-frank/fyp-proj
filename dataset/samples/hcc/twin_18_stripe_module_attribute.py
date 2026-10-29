import os

import stripe

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]


def refund(charge_id):
    return stripe.Refund.create(charge=charge_id)
