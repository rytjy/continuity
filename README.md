# continuity

A six-month public record, written once a week and never edited afterwards.

## What this is

One entry per week, starting 2026-11-11 and running to 2027-05-11. Each entry states what actually happened that week in two lines of work:

- **A paper forward test** of one fixed rule on ETH: long after a 24h drop of 2% or more, hold 24h, 29bp round-trip cost, starting equity $74.69. Simulated, not live money.
- **Upstream code contributions**: pull requests opened, merged, or reviewed, with links.

## What this is not

Not a track record, not a claim of profitability, not advice. The forward test has four trades. Nothing here has been validated out of sample.

## How to check it

- Every entry is appended by `scripts/weekly.py`, never by hand.
- Each entry carries `prev_sha256`: the SHA-256 of the file *before* that entry was appended. Edit any earlier entry and every later hash breaks.
- Git history is the second witness. Entries are committed at the time they are written.
- The forward-test numbers come from `trades.csv` and `state.json` in the source tree; the PR lines come from the GitHub API under the account that owns this repo.

## Why

Public work fails as a way to reach people — 157 views, 0 replies is the measured number in my notes. What it can still do is produce a record that does not depend on anyone trusting me: dated, hash-chained, checkable. Six months of it is a different claim from one good week.

## Rule

Append only. If something was wrong, the next entry says so; the earlier entry stays.

