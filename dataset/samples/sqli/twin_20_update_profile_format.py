def update_bio(conn, user_id, bio):
    cur = conn.cursor()
    sql = "UPDATE profiles SET bio = %s WHERE user_id = %s"
    cur.execute(sql, (bio, user_id))
    conn.commit()
