# crawler.py
import requests
import sqlite3
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

START_URL = "https://en.wikipedia.org/wiki/Computer_security"
MAX_PAGES = 10
DELAY = 1

# --- database ---
conn = sqlite3.connect("pages.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS pages (
    url TEXT PRIMARY KEY,
    content TEXT
)
""")
conn.commit()

visited = set()

def same_domain(url):
    return urlparse(url).netloc == urlparse(START_URL).netloc

def crawl(url):
    if url in visited or len(visited) >= MAX_PAGES:
        return

    visited.add(url)
    print("Crawling:", url)

    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                ),
                "Accept": "text/html",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=10,
            allow_redirects=True
        )
    except Exception as e:
        print("Request failed:", e)
        return

    print("  status:", r.status_code)
    print("  response length:", len(r.text))

    soup = BeautifulSoup(r.content, "html.parser")

    text = soup.get_text(" ", strip=True)
    cur.execute(
        "INSERT OR IGNORE INTO pages VALUES (?, ?)",
        (url, text)
    )
    conn.commit()

    links = soup.find_all("a", href=True)
    print("  found links:", len(links))

    for a in links:
        href = a["href"]

        # Wikipedia-safe filtering
        if not href.startswith("/wiki/"):
            continue
        if ":" in href:
            continue
        if "#" in href:
            continue

        link = urljoin(url, href)   # IMPORTANT FIX

        if same_domain(link):
            crawl(link)

    time.sleep(DELAY)

crawl(START_URL)
conn.close()

print("Done. Pages crawled:", len(visited))
