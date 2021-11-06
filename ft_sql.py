import sqlite3

conn = sqlite3.connect("test.db",check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS test
    (id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    title text,
    artist text)
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS 'stories'
    ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    'item' INTEGER,
    'name' text,
    'text' text,
    'author' text,
    'author_id' INTEGER NOT NULL,
    'author_username' text)
""")
conn.commit()

def sql_execute(str: str):
    cursor.execute(str)
    t = cursor.fetchall()
    conn.commit()
    return t


if __name__ == "__main__":
    cursor.execute("""
        INSERT INTO stories (name, text, author, author_id, author_username)
        VALUES(?,?,?,?,?)
    """, ["Test story",
          "Почему люди какают? Вопрос интересный, но мне лень писать про него, они какают и все",
          "Tester Tester",
          11111111,
          "@tester"])
    conn.commit()