def update_email(cursor, user_id, email):
    cursor.execute(
        "UPDATE users SET email = %(email)s WHERE id = %(id)s",
        {"email": email, "id": user_id},
    )
