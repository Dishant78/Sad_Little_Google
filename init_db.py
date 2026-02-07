import sqlite3

conn = sqlite3.connect("search.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS pages (
    url TEXT PRIMARY KEY,
    content TEXT,
    last_crawled REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS index_table (
    word TEXT,
    url TEXT,
    count INTEGER,
    PRIMARY KEY (word, url)
)
""")

conn.commit()
conn.close()
print("DB ready")
