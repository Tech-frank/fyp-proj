from shop.models import Customer


def customers_named(name):
    return list(Customer.objects.filter(last_name__iexact=name).values("id", "email"))
