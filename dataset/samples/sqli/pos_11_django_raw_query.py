from shop.models import Product


def products_in_category(category_slug):
    return list(Product.objects.raw(
        f"SELECT * FROM shop_product WHERE category_slug = '{category_slug}'"
    ))
