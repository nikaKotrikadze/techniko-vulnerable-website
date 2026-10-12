#!/usr/bin/env python3
"""
================================================================================
  INTENTIONALLY VULNERABLE WEB APP  --  FOR LOCAL LEARNING ONLY
================================================================================

This is a teaching sandbox in the spirit of DVWA / OWASP Juice Shop / WebGoat.
Every vulnerability here is DELIBERATE. Each one is marked with a `# VULN:`
comment that names the flaw, shows how to exploit it, and shows the fix.

  >>> DO NOT deploy this. DO NOT put it on a public IP. DO NOT use real data. <<<

It binds to 127.0.0.1 (localhost) on purpose so it is only reachable from your
own machine. Zero dependencies -- Python 3 standard library only.

Run:        python3 app.py
Then open:  http://127.0.0.1:8000

The point is to SEE the bugs and then practice fixing them. Fixes are written
in the comment right above each vulnerable line.
================================================================================
"""

import html
import http.cookies
import sqlite3
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

DB = ":memory:"
_conn = sqlite3.connect(DB, check_same_thread=False)


def init_db():
    c = _conn.cursor()
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, secret TEXT)")
    # VULN (Sensitive data): passwords stored in plaintext.
    #   FIX: store a salted hash, e.g. hashlib.scrypt / bcrypt / argon2, never the password itself.
    c.executemany(
        "INSERT INTO users (username, password, secret) VALUES (?, ?, ?)",
        [
            ("admin", "admin123", "The admin's secret: the cake is a lie."),
            ("alice", "password", "Alice keeps her diary in /dev/null."),
            ("bob", "hunter2", "Bob still uses hunter2 everywhere."),
        ],
    )
    c.execute("CREATE TABLE comments (id INTEGER PRIMARY KEY, body TEXT)")
    _conn.commit()


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vulnerable Demo (localhost only)</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #f4f5f7; --card: #ffffff; --ink: #1a1c1f; --muted: #5b6168;
    --line: #e2e5ea; --accent: #3b5bdb; --accent-ink: #fff;
    --danger: #b02a37; --code-bg: #eef0f4; --out-bg: #f0f2f6;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #15171c; --card: #1e2128; --ink: #e8eaed; --muted: #9aa1ab;
      --line: #2c313a; --accent: #5c7cfa; --code-bg: #272b33; --out-bg: #242831;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font: 15px/1.6 system-ui, -apple-system, Segoe UI, sans-serif;
    background: var(--bg); color: var(--ink); margin: 0; padding: 0 16px 64px;
  }}
  .wrap {{ max-width: 820px; margin: 0 auto; }}
  .banner {{
    background: var(--danger); color: #fff; text-align: center;
    padding: 10px 16px; font-weight: 600; font-size: 0.9rem;
    margin: 0 -16px 0; letter-spacing: 0.01em;
  }}
  header.hero {{ padding: 36px 0 8px; }}
  header.hero h1 {{ font-size: 1.9rem; margin: 0 0 6px; letter-spacing: -0.02em; }}
  header.hero p {{ color: var(--muted); margin: 0; max-width: 60ch; }}
  header.hero code {{ font-size: 0.85em; }}
  .grid {{ display: grid; grid-template-columns: 1fr; gap: 18px; margin-top: 28px; }}
  @media (min-width: 680px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
  .card {{
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 20px; box-shadow: 0 1px 2px #0000000d; display: flex; flex-direction: column;
  }}
  .card.wide {{ grid-column: 1 / -1; }}
  .tag {{
    display: inline-block; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.06em;
    text-transform: uppercase; color: var(--accent); background: var(--code-bg);
    padding: 3px 9px; border-radius: 999px; margin-bottom: 10px; align-self: flex-start;
  }}
  .card h2 {{ font-size: 1.1rem; margin: 0 0 4px; }}
  .card .desc {{ color: var(--muted); font-size: 0.88rem; margin: 0 0 16px; }}
  form.fields {{ display: flex; flex-direction: column; gap: 10px; }}
  label {{ display: flex; flex-direction: column; gap: 4px; font-size: 0.8rem;
    font-weight: 600; color: var(--muted); }}
  input {{
    font: inherit; padding: 9px 11px; border: 1px solid var(--line);
    border-radius: 9px; background: var(--bg); color: var(--ink); width: 100%;
  }}
  input:focus {{ outline: 2px solid var(--accent); outline-offset: 0; border-color: transparent; }}
  .row {{ display: flex; gap: 8px; }}
  .row input {{ flex: 1; }}
  button {{
    font: inherit; font-weight: 600; padding: 9px 18px; cursor: pointer;
    background: var(--accent); color: var(--accent-ink); border: 0;
    border-radius: 9px; align-self: flex-start;
  }}
  button:hover {{ filter: brightness(1.07); }}
  code {{ background: var(--code-bg); padding: 1px 6px; border-radius: 5px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .hint {{ font-size: 0.82rem; color: var(--muted); margin: 12px 0 0; }}
  .out {{
    background: var(--out-bg); border: 1px solid var(--line); border-radius: 9px;
    padding: 12px; margin-top: 14px; white-space: pre-wrap; word-break: break-word;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.82rem;
  }}
  .comments {{ margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }}
  .comments:empty::after {{ content: "No comments yet."; color: var(--muted); font-size: 0.85rem; }}
  .comments .out {{ margin-top: 0; }}
  footer {{ text-align: center; color: var(--muted); font-size: 0.8rem; margin-top: 40px; }}
</style></head><body>
<div class="banner">⚠ Intentionally vulnerable teaching app — runs on localhost only. Never deploy.</div>
<div class="wrap">
<header class="hero">
  <h1>Vulnerable Website Demo</h1>
  <p>A security sandbox with five classic web vulnerabilities to exploit and fix.
  Each flaw is labeled in <code>app.py</code> with a <code>#&nbsp;VULN</code> comment —
  the exploit and the fix sit right next to the code.</p>
</header>

<div class="grid">
  <div class="card">
    <span class="tag">1 · SQL Injection</span>
    <h2>Login</h2>
    <p class="desc">Sign in to see your account secret.</p>
    <form class="fields" method="post" action="/login">
      <label>Username
        <input name="username" placeholder="username" value="admin" autocomplete="off">
      </label>
      <label>Password
        <input name="password" type="password" placeholder="password" autocomplete="off">
      </label>
      <button>Log in</button>
    </form>
    <p class="hint">Try password <code>' OR '1'='1</code> — logs in with no real password.</p>
    {login_out}
  </div>

  <div class="card">
    <span class="tag">2 · Reflected XSS</span>
    <h2>Search</h2>
    <p class="desc">Search the site. Your term is echoed back.</p>
    <form class="fields" method="get" action="/search">
      <label>Search query
        <div class="row">
          <input name="q" placeholder="search for anything…">
          <button>Search</button>
        </div>
      </label>
    </form>
    <p class="hint">Try <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> — it executes.</p>
    {search_out}
  </div>

  <div class="card">
    <span class="tag">4 · Command Injection</span>
    <h2>Network ping tool</h2>
    <p class="desc">Check if a host is reachable.</p>
    <form class="fields" method="get" action="/ping">
      <label>Host
        <div class="row">
          <input name="host" placeholder="127.0.0.1" value="127.0.0.1">
          <button>Ping</button>
        </div>
      </label>
    </form>
    <p class="hint">Try <code>127.0.0.1; echo PWNED</code> — runs your shell command.</p>
    {ping_out}
  </div>

  <div class="card">
    <span class="tag">5 · Path Traversal</span>
    <h2>File viewer</h2>
    <p class="desc">View a document from the site folder.</p>
    <form class="fields" method="get" action="/view">
      <label>Filename
        <div class="row">
          <input name="file" placeholder="welcome.txt" value="welcome.txt">
          <button>View</button>
        </div>
      </label>
    </form>
    <p class="hint">Try <code>../../../../etc/passwd</code> — escapes the folder.</p>
    {view_out}
  </div>

  <div class="card wide">
    <span class="tag">3 · Stored XSS</span>
    <h2>Guestbook</h2>
    <p class="desc">Leave a comment. Everyone who visits sees it — rendered as-is.</p>
    <form class="fields" method="post" action="/comment">
      <label>Your comment
        <div class="row">
          <input name="body" placeholder="say something nice…">
          <button>Post</button>
        </div>
      </label>
    </form>
    <p class="hint">Try posting <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> — it runs for every visitor.</p>
    <div class="comments">{comments_out}</div>
  </div>
</div>

<footer>Teaching sandbox · bound to 127.0.0.1 · read <code>app.py</code> for the fixes</footer>
</div>
</body></html>"""


def render(**kw):
    for k in ("login_out", "search_out", "comments_out", "ping_out", "view_out"):
        kw.setdefault(k, "")
    # comments are rendered separately so they always show
    rows = _conn.execute("SELECT body FROM comments ORDER BY id DESC LIMIT 20").fetchall()
    # VULN (Stored XSS): comment bodies written to the page without escaping.
    #   FIX: html.escape(body) before inserting into HTML.
    kw["comments_out"] = "".join(f'<div class="out">{r[0]}</div>' for r in rows)
    return PAGE.format(**kw)


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, status=200, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)

        if u.path == "/":
            self._send(render())

        elif u.path == "/search":
            term = q.get("q", [""])[0]
            # VULN (Reflected XSS): user input echoed straight into HTML.
            #   FIX: out = html.escape(term)
            out = f'<div class="out">Results for: {term}</div>' if term else ""
            self._send(render(search_out=out))

        elif u.path == "/ping":
            host = q.get("host", [""])[0]
            out = ""
            if host:
                # VULN (Command Injection): shell=True with user input in the string.
                #   FIX: subprocess.run(["ping","-c","1",host], shell=False) and validate host.
                try:
                    res = subprocess.run(
                        f"ping -c 1 {host}", shell=True,
                        capture_output=True, text=True, timeout=5,
                    )
                    out = f'<div class="out">{html.escape(res.stdout + res.stderr)}</div>'
                except Exception as e:
                    out = f'<div class="out">error: {html.escape(str(e))}</div>'
            self._send(render(ping_out=out))

        elif u.path == "/view":
            name = q.get("file", [""])[0]
            out = ""
            if name:
                # VULN (Path Traversal): path built from user input with no containment.
                #   FIX: only allow a known basename, reject "/" and "..", or use
                #        os.path.realpath and verify it stays inside the base dir.
                try:
                    with open(name, "r", errors="replace") as f:
                        data = f.read(4000)
                    out = f'<div class="out">{html.escape(data)}</div>'
                except Exception as e:
                    out = f'<div class="out">error: {html.escape(str(e))}</div>'
            self._send(render(view_out=out))

        else:
            self._send(render(), status=404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        form = {k: v[0] for k, v in urllib.parse.parse_qs(body).items()}
        u = urllib.parse.urlparse(self.path)

        if u.path == "/login":
            user = form.get("username", "")
            pw = form.get("password", "")
            # VULN (SQL Injection): query built by string concatenation.
            #   FIX: parametrize ->
            #        _conn.execute("SELECT ... WHERE username=? AND password=?", (user, pw))
            sql = f"SELECT username, secret FROM users WHERE username='{user}' AND password='{pw}'"
            try:
                rows = _conn.execute(sql).fetchall()
            except Exception as e:
                rows = []
                out = f'<div class="out">SQL error: {html.escape(str(e))}</div>'
                self._send(render(login_out=out))
                return
            if rows:
                # VULN (Sensitive data exposure): dumping each user's secret on login.
                lines = "\n".join(f"{r[0]}: {r[1]}" for r in rows)
                # VULN (predictable session): fixed, guessable cookie value.
                #   FIX: use secrets.token_urlsafe() and set HttpOnly, Secure, SameSite.
                ck = http.cookies.SimpleCookie()
                ck["session"] = "logged-in-as-" + (rows[0][0] or "user")
                out = f'<div class="out">Logged in!\n{html.escape(lines)}</div>'
                self._send(render(login_out=out),
                           headers={"Set-Cookie": ck["session"].OutputString()})
            else:
                self._send(render(login_out='<div class="out">Invalid credentials.</div>'))

        elif u.path == "/comment":
            body_text = form.get("body", "")
            if body_text:
                # VULN (Stored XSS): raw input persisted, later rendered unescaped (see render()).
                _conn.execute("INSERT INTO comments (body) VALUES (?)", (body_text,))
                _conn.commit()
            self._send(render())
        else:
            self._send(render(), status=404)

    def log_message(self, *a):
        pass  # keep the console quiet


if __name__ == "__main__":
    init_db()
    with open("welcome.txt", "w") as f:
        f.write("This is the intended file for the viewer demo. Try to escape this folder.\n")
    print("Vulnerable demo running at http://127.0.0.1:8000  (localhost only, Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
