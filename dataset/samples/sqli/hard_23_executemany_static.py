def insert_readings(cursor, readings):
    cursor.executemany("INSERT INTO readings (sensor, value) VALUES (?, ?)", readings)
