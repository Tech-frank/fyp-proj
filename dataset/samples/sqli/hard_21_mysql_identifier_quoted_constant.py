REPORT_VIEW = "v_daily_revenue"


def refresh_report(cursor):
    cursor.execute("REFRESH MATERIALIZED VIEW %s" % REPORT_VIEW)
