# app.py
from flask import Flask, request
import sqlite3
import re

app = Flask(__name__)

def tokenize(text):
    return re.findall(r"[a-z]{2,}", text.lower())

def search(query):
    if not query:
        return []

    words = tokenize(query)
    conn = sqlite3.connect("pages.db")
    cur = conn.cursor()

    scores = {}
    snippets = {}

    for word in words:
        cur.execute(
            "SELECT url, count FROM index_table WHERE word = ?",
            (word,)
        )
        for url, count in cur.fetchall():
            scores[url] = scores.get(url, 0) + count

            # fetch snippet once
            if url not in snippets:
                cur.execute(
                    "SELECT content FROM pages WHERE url = ?",
                    (url,)
                )
                row = cur.fetchone()
                if row:
                    text = row[0]
                    idx = text.lower().find(word)
                    if idx != -1:
                        snippets[url] = text[max(0, idx-80): idx+160] + "..."
                    else:
                        snippets[url] = text[:200] + "..."

    conn.close()

    results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(url, score, snippets.get(url, "")) for url, score in results]


@app.route("/")
def home():
    q = request.args.get("q", "")
    results = search(q) if q else []

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>sad little Google</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f8f9fa;
            margin: 0;
        }}
        .container {{
            max-width: 800px;
            margin: 80px auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .logo {{
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }}
        .logo span:nth-child(1) {{ color: #4285F4; }}
        .logo span:nth-child(2) {{ color: #DB4437; }}
        .logo span:nth-child(3) {{ color: #F4B400; }}
        .logo span:nth-child(4) {{ color: #4285F4; }}
        .logo span:nth-child(5) {{ color: #0F9D58; }}
        .logo span:nth-child(6) {{ color: #DB4437; }}

        form {{
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }}
        input[type="text"] {{
            width: 70%;
            padding: 12px 16px;
            font-size: 16px;
            border-radius: 24px;
            border: 1px solid #ccc;
            outline: none;
        }}
        button {{
            margin-left: 10px;
            padding: 12px 20px;
            border-radius: 24px;
            border: none;
            background: #4285F4;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }}
        button:hover {{
            background: #357ae8;
        }}
        .result {{
            margin-bottom: 25px;
        }}
        .result a {{
            font-size: 18px;
            color: #1a0dab;
            text-decoration: none;
        }}
        .result a:hover {{
            text-decoration: underline;
        }}
        .url {{
            font-size: 14px;
            color: #006621;
        }}
        .snippet {{
            font-size: 14px;
            color: #545454;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <span>S</span><span>a</span><span>d</span>
            <span>L</span><span>i</span><span>t</span><span>t</span><span>t</span><span>e</span>
            <span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span>
        </div>

        <form>
            <input type="text" name="q" value="{q}" placeholder="Search the tiny internet...">
            <button type="submit">Search</button>
        </form>

        {"".join(f'''
        <div class="result">
            <a href="{url}">{url}</a>
            <div class="url">{url}</div>
            <div class="snippet">{snippet}</div>
        </div>
        ''' for url, score, snippet in results[:10])}
    </div>
</body>
</html>
"""
    
if __name__ == "__main__":
    app.run(debug=True)
