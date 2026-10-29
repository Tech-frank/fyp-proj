import sqlite3


def main():
    name = input("Book title to search: ")
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("SELECT title, author FROM books WHERE title = '%s'" % name)
    for title, author in cur.fetchall():
        print(f"{title} by {author}")


if __name__ == "__main__":
    main()
