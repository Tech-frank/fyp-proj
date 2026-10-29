from decimal import Decimal, ROUND_HALF_UP

VAT = Decimal("0.075")


def gross(net):
    return (Decimal(net) * (1 + VAT)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
