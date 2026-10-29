def delete_comment(db, comment_id, author):
    cur = db.cursor()
    cur.execute("DELETE FROM comments WHERE id = {} AND author = '{}'".format(comment_id, author))
    db.commit()
    return cur.rowcount
