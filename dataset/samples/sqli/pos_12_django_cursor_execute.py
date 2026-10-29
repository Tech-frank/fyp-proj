from django.db import connection


def mark_shipped(order_ref):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE orders SET status = 'shipped' WHERE ref = '%s'" % order_ref)
