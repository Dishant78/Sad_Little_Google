# indexer.py
import sqlite3
import re
from collections import defaultdict

conn = sqlite3.connect("pages.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS index_table (
    word TEXT,
    url TEXT,
    count INTEGER
)
""")
conn.commit()

cur.execute("SELECT url, content FROM pages")

index = defaultdict(lambda: defaultdict(int))

def tokenize(text):
    return re.findall(r"[a-zA-Z]{2,}", text.lower())

for url, content in cur.fetchall():
    for word in tokenize(content):
        index[word][url] += 1

for word, urls in index.items():
    for url, count in urls.items():
        cur.execute(
            "INSERT INTO index_table VALUES (?, ?, ?)",
            (word, url, count)
        )

conn.commit()
conn.close()
print("Index built.")
