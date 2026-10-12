# Vulnerable Website Demo (teaching sandbox)

An **intentionally vulnerable** web app for learning, in the spirit of
[DVWA](https://github.com/digininja/DVWA), [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/),
and [WebGoat](https://owasp.org/www-project-webgoat/). Every flaw is deliberate
and labeled in the code.

> ⚠️ **For local learning only.** It binds to `127.0.0.1` on purpose so only your
> machine can reach it. **Do not deploy it, do not expose it to a network, and do
> not put real data in it.** An intentionally vulnerable app is dangerous if it's
> reachable by anyone else.

## Run

```bash
python3 app.py
```

Then open http://127.0.0.1:8000 — no dependencies, Python 3 stdlib only. `Ctrl+C` to stop.

## What's inside

Each vulnerability has a `# VULN:` comment in [`app.py`](app.py) naming the flaw,
the exploit, and the fix.

| # | Vulnerability | Where | Try it |
|---|---------------|-------|--------|
| 1 | SQL Injection | `/login` | password `' OR '1'='1` logs in + dumps secrets |
| 2 | Reflected XSS | `/search` | `q=<script>alert(1)</script>` |
| 3 | Stored XSS | `/comment` | post `<script>alert(1)</script>` |
| 4 | Command Injection | `/ping` | host `127.0.0.1; echo PWNED` |
| 5 | Path Traversal | `/view` | file `../../../../etc/passwd` |

Also shown: plaintext password storage, sensitive-data exposure on login, and a
predictable session cookie.

## How to use it

1. Trigger each exploit above and watch what happens.
2. Open `app.py`, find the matching `# VULN` comment, and read the fix.
3. Apply the fix and confirm the exploit no longer works — that's the exercise.
