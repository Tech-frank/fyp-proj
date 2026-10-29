from shop.models import Product


def products_in_category(category_slug):
    return list(Product.objects.raw(
        "SELECT * FROM shop_product WHERE category_slug = %s", [category_slug]
    ))
