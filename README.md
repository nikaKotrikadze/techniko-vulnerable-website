# TechNiko — Vulnerable Website Demo 🧪

An **intentionally vulnerable** web app you can run on your own machine to learn
how common web security bugs work — and to watch an AI security-audit skill find
them for you.

Think of it as a practice dummy, in the same spirit as
[DVWA](https://github.com/digininja/DVWA),
[OWASP Juice Shop](https://owasp.org/www-project-juice-shop/), and
[WebGoat](https://owasp.org/www-project-webgoat/). Every single flaw in here is
on purpose, and every flaw is labeled in the code with a `# VULN` comment that
shows the exploit **and** the fix.

> ⚠️ **This is a learning tool. Run it on your own computer only.**
> It binds to `127.0.0.1` (localhost) on purpose, so only *your* machine can
> reach it — nobody else can touch your copy. **Never deploy it to a public
> server or put real data in it.** Running it locally is safe and is the whole
> point; hosting it publicly would turn these practice bugs into real ones.

---

## 🎥 What this is for

In the video I pair this demo with a **Claude skill that audits code for
security vulnerabilities** — Cloudflare's open-source **security-audit** skill:

👉 **https://github.com/cloudflare/security-audit-skill**

That skill turns your coding agent into a security auditor: you point it at a
codebase and it hunts for vulnerabilities, validates each one, and writes up a
report. **This website is the test target** — a small, deliberately broken
codebase you can run the skill against to see it catch real bugs (SQL injection,
XSS, command injection, and more) in `app.py`.

So the flow is:

1. Clone this vulnerable demo.
2. Install Cloudflare's security-audit skill.
3. Run the skill against this repo and watch it find the planted vulnerabilities.
4. Open `app.py` and compare its findings to the labeled `# VULN` comments.

---

## 1️⃣ Install & run the vulnerable website

No dependencies — just Python 3 (standard library only).

```bash
git clone https://github.com/nikaKotrikadze/techniko-vulnerable-website.git
cd techniko-vulnerable-website
python3 app.py
```

Then open **http://127.0.0.1:8000** in your browser. Press `Ctrl+C` to stop.

### The vulnerabilities (try them yourself)

| # | Vulnerability | Where | Try this |
|---|---------------|-------|----------|
| 1 | SQL Injection | Login | password `' OR '1'='1` → logs in with no real password + dumps secrets |
| 2 | Reflected XSS | Search | `<script>alert(1)</script>` |
| 3 | Stored XSS | Guestbook | post `<script>alert(1)</script>` |
| 4 | Command Injection | Ping tool | host `127.0.0.1; echo PWNED` |
| 5 | Path Traversal | File viewer | file `../../../../etc/passwd` |

Also inside: plaintext password storage, secret exposure on login, and a
predictable session cookie. Each one is labeled in [`app.py`](app.py) with a
`# VULN` comment that includes the fix.

---

## 2️⃣ Install the security-audit skill (the thing that finds the bugs)

Cloudflare's skill installs with the [Skills CLI](https://skills.sh). Install it
globally (available to your agent everywhere):

```bash
npx skills add https://github.com/cloudflare/security-audit-skill \
  --skill security-audit \
  --global
```

(Drop `--global` to install it just for the current project. Run
`npx skills --help` for options.)

**Requirements** (from Cloudflare's repo): a coding agent whose model supports
tool use and sub-agents, and Node.js for the skill's validators.

---

## 3️⃣ Run the audit against this website

Point your coding agent at this cloned folder and ask it to audit the code:

```
security audit this codebase
```

The skill maps the code, hunts for vulnerabilities, independently verifies each
one, and writes up a report. Then open `app.py` and check its findings against
the `# VULN` comments — that's the fun part: seeing the AI find the exact bugs
that were planted on purpose.

> Note: the skill reads and reasons about the **source code** — it's a code
> auditor, not a live attack tool pointed at a running URL. That's exactly why
> this small, self-contained `app.py` makes a clean test target.

---

## 🛠️ How to use it to actually learn

1. Trigger each exploit in the table above and watch what happens.
2. Run the security-audit skill and read what it reports.
3. Open `app.py`, find the matching `# VULN` comment, and apply the fix.
4. Restart and confirm the exploit no longer works. That's the exercise. ✅

---

## 📄 License & credit

This demo: free to use for learning. Cloudflare's
[security-audit-skill](https://github.com/cloudflare/security-audit-skill) is
MIT-licensed and maintained by Cloudflare — all credit to them for that tool.

Made for the **TechNiko** channel.
