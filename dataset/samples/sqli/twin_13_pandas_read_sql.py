import pandas as pd


def sales_for_region(engine, region):
    return pd.read_sql(
        "SELECT month, revenue FROM sales WHERE region = %(region)s", engine, params={"region": region}
    )
