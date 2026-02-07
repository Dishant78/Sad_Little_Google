import requests, time, re, sqlite3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

START_URL = "https://paruluniversity.ac.in"
MAX_PAGES = 50
visited = set()
queue = [START_URL]

def tokenize(text):
    return re.findall(r"[a-z]{2,}", text.lower())

conn = sqlite3.connect("search.db", check_same_thread=False)
cur = conn.cursor()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
    )
}

while queue and len(visited) < MAX_PAGES:
    url = queue.pop(0)
    if url in visited:
        continue

    print("Crawling:", url)
    visited.add(url)

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except:
        continue

    soup = BeautifulSoup(r.content, "html.parser")
    text = soup.get_text(" ", strip=True)

    cur.execute(
        "INSERT OR REPLACE INTO pages VALUES (?, ?, ?)",
        (url, text, time.time())
    )

    words = tokenize(text)
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    for w, c in freq.items():
        cur.execute(
            "INSERT OR REPLACE INTO index_table VALUES (?, ?, ?)",
            (w, url, c)
        )

    conn.commit()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("/wiki/"):
            continue
        if ":" in href or "#" in href:
            continue
        link = urljoin(url, href)
        if urlparse(link).netloc == "en.wikipedia.org":
            queue.append(link)

    time.sleep(2)

print("Crawler running finished")
