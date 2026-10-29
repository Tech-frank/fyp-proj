def update_bio(conn, user_id, bio):
    cur = conn.cursor()
    sql = "UPDATE profiles SET bio = '{}' WHERE user_id = {}".format(bio, user_id)
    cur.execute(sql)
    conn.commit()
