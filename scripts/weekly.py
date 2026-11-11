#!/usr/bin/env python3
"""Append one dated entry to RECORD.md, hash-chained, then commit and push.

Data sources:
  - forward test: <workspace>/trading_research/fwd_eth_drop/{state.json,trades.csv}
  - GitHub: pull requests authored by the repo owner

Run: python3 scripts/weekly.py [--dry-run]
"""
import hashlib, json, os, subprocess, sys, urllib.request
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORD = os.path.join(REPO, "RECORD.md")
FWD = os.environ.get("FWD_DIR", "/root/.openclaw/workspace/trading_research/fwd_eth_drop")
TOKEN = open("/root/.secrets/github_pat").read().strip()
OWNER = "rytjy"
PROXY = {"http": "http://127.0.0.1:3128", "https": "http://127.0.0.1:3128"}
DRY = "--dry-run" in sys.argv


def gh(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "continuity", "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + TOKEN})
    op = urllib.request.build_opener(urllib.request.ProxyHandler(PROXY))
    return json.loads(op.open(req, timeout=30).read().decode())


def sha_prev(text):
    return hashlib.sha256(text.encode()).hexdigest()


def forward():
    try:
        st = json.load(open(os.path.join(FWD, "state.json")))
        rows = open(os.path.join(FWD, "trades.csv")).read().strip().split("\n")[1:]
        last = rows[-1].split(",") if rows else None
        return st, last
    except Exception as e:
        return None, str(e)


def prs():
    try:
        q = gh("https://api.github.com/search/issues?q=author:%s+type:pr+created:>2026-09-01&per_page=100" % OWNER)
        items = q.get("items", [])
        merged = [i for i in items if i.get("pull_request", {}).get("merged_at")]
        open_ = [i for i in items if i["state"] == "open"]
        return items, merged, open_
    except Exception:
        return [], [], []


def entry():
    st, last = forward()
    items, merged, open_ = prs()
    now = datetime.now(timezone.utc)
    body = open(RECORD).read() if os.path.exists(RECORD) else ""
    lines = []
    lines.append("## %s" % now.strftime("%Y-%m-%d"))
    lines.append("")
    if st:
        eq = st.get("equity")
        lines.append("- Forward test (ETH 24h-drop, paper, start $%.2f): equity **$%.2f**, %d closed trades, %d win(s), position %s." % (
            st.get("initial", 0), eq, st.get("trades", 0), st.get("wins", 0),
            "open" if st.get("position") else "flat"))
        if last and len(last) >= 7:
            lines.append("  - last exit %s: %.2f -> %.2f, PnL $%s" % (last[1][:16], float(last[2]), float(last[3]), last[6]))
    else:
        lines.append("- Forward test: data unavailable this week (%s)." % (last if isinstance(last, str) else "no file"))
    lines.append("- Upstream PRs (author %s): %d total, %d merged, %d open." % (OWNER, len(items), len(merged), len(open_)))
    for i in merged[-3:]:
        repo = i["repository_url"].split("/repos/")[-1]
        lines.append("  - merged %s#%d %s" % (repo, i["number"], i["title"][:70]))
    for i in open_[:3]:
        repo = i["repository_url"].split("/repos/")[-1]
        lines.append("  - open %s#%d %s" % (repo, i["number"], i["title"][:70]))
    lines.append("- prev_sha256: `%s`" % sha_prev(body))
    lines.append("")
    return "\n".join(lines)


def record_failure(err):
    """Failures must be visible in the ledger that every session reads, not only in a chat."""
    pend = os.environ.get("PENDING_FILE", "/root/.openclaw/workspace/LEDGER_PENDING.md")
    msg = str(err)[:400].replace("\n", " ")
    try:
        with open(pend, "a") as f:
            f.write("\n%s | continuity weekly push failed | %s<!-- project: path:/root/.openclaw/workspace -->\n" % (
                datetime.now().strftime("%Y-%m-%d %H:%M"), msg))
    except Exception:
        pass


def main():
    text = entry()
    print(text)
    if DRY:
        return
    with open(RECORD, "a") as f:
        f.write(text)
    subprocess.run(["git", "-C", REPO, "add", "RECORD.md"], check=True)
    msg = "record: " + datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subprocess.run(["git", "-C", REPO, "commit", "-m", msg], check=True)
    subprocess.run(["git", "-C", REPO, "push"], check=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        record_failure(e)
        raise

