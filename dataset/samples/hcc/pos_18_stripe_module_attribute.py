import stripe

stripe.api_key = "sk_live_4eC39HqLyjWDarjtT1zdp7dc"


def refund(charge_id):
    return stripe.Refund.create(charge=charge_id)
