import datetime


def events_last_week(cursor):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=7)
    cursor.execute("SELECT name, day FROM events WHERE day BETWEEN ? AND ?", (start, end))
    return cursor.fetchall()
