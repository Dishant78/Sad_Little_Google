# app.py
from flask import Flask, request, jsonify
import sqlite3, time, re

app = Flask(__name__)

def tokenize(q):
    return re.findall(r"[a-z]{2,}", q.lower())

def search(q):
    words = tokenize(q)
    if not words:
        return []

    conn = sqlite3.connect("search.db")
    cur = conn.cursor()

    page_scores = {}
    page_matches = {}

    for w in words:
        cur.execute(
            "SELECT url, count FROM index_table WHERE word=?",
            (w,)
        )
        for url, c in cur.fetchall():
            page_scores[url] = page_scores.get(url, 0) + c
            page_matches.setdefault(url, set()).add(w)

    results = []
    for url, score in page_scores.items():
        matched_words = len(page_matches[url])
        coverage = matched_words / len(words)   # 🔥 key improvement

        cur.execute(
            "SELECT content, last_crawled FROM pages WHERE url=?",
            (url,)
        )
        content, ts = cur.fetchone()

        length_penalty = max(1, len(content) / 1000)
        final_score = (score * coverage) / length_penalty

        results.append((final_score, url, content, ts))

    conn.close()

    results.sort(reverse=True)

    formatted = []
    for score, url, content, ts in results[:10]:
        snippet = content[:200] + "..."
        age = int(time.time() - ts)
        formatted.append({
            "url": url,
            "snippet": snippet,
            "fresh": age
        })

    return formatted


@app.route("/search")
def api_search():
    q = request.args.get("q", "")
    return jsonify(search(q))


@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Sad Little Google</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #fff;
    margin: 0;
}

.container {
    max-width: 700px;
    margin: 120px auto;
    text-align: center;
}

.logo {
    font-size: 48px;
    font-weight: bold;
    margin-bottom: 30px;
}

.logo span:nth-child(1) { color: #4285F4; }
.logo span:nth-child(2) { color: #DB4437; }
.logo span:nth-child(3) { color: #F4B400; }
.logo span:nth-child(4) { color: #4285F4; }
.logo span:nth-child(5) { color: #0F9D58; }
.logo span:nth-child(6) { color: #DB4437; }
.logo span:nth-child(7) { color: #555; }
.logo span:nth-child(8) { color: #555; }
.logo span:nth-child(9) { color: #555; }
.logo span:nth-child(10){ color: #555; }
.logo span:nth-child(11){ color: #555; }
.logo span:nth-child(12){ color: #555; }
.logo span:nth-child(13){ color: #555; }

input {
    width: 100%;
    padding: 14px 18px;
    font-size: 18px;
    border-radius: 24px;
    border: 1px solid #dfe1e5;
    outline: none;
}

input:focus {
    box-shadow: 0 1px 6px rgba(32,33,36,.28);
}

.results {
    text-align: left;
    margin-top: 40px;
}

.result {
    margin-bottom: 28px;
}

.result a {
    font-size: 18px;
    color: #1a0dab;
    text-decoration: none;
}

.result a:hover {
    text-decoration: underline;
}

.snippet {
    font-size: 14px;
    color: #545454;
}

.fresh {
    font-size: 12px;
    color: #777;
}
</style>
</head>

<body>
<div class="container">
    <div class="logo">
        <span>S</span><span>a</span><span>d</span>
        <span>L</span><span>i</span><span>t</span><span>t</span><span>l</span><span>e</span>
        <span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span>
    </div>

    <input id="q" placeholder="Search the tiny, slightly miserable web">

    <div class="results" id="results"></div>
</div>

<script>
const q = document.getElementById("q")
const res = document.getElementById("results")

q.addEventListener("input", () => {
    fetch("/search?q=" + q.value)
        .then(r => r.json())
        .then(data => {
            res.innerHTML = ""
            data.forEach(d => {
                res.innerHTML += `
                    <div class="result">
                        <a href="${d.url}">${d.url}</a>
                        <div class="snippet">${d.snippet}</div>
                        <div class="fresh">Indexed ${d.fresh}s ago</div>
                    </div>
                `
            })
        })
})
</script>
</body>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True)
