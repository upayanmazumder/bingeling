# Work log

| Date | Work | Check |
|---|---|---|
| 2026-10-22 | Audited the bootstrap repo and wrote the issue plan. | GitHub goal #1 contains seven milestone epics and their tasks. |
| 2026-10-22 | Started the complete project implementation. | Data, queries, and report work have separate owners. |
| 2026-10-22 | Added Compose health check, an empty-database demo script, a query runner, and CI. | Full-flow verification follows data and query integration. |
| 2026-10-22 | Generated the seed data from Netflix and MovieLens archives. Fixed the email domain to `example.com`. | Validator reports `valid: true`. |
| 2026-10-22 | Fixed the text index and switched queries to file mode. | `bash scripts/demo.sh` passed all 10 queries from an empty volume. |
| 2026-10-22 | Captured 11 terminal screenshots in Xvfb and built the report. | `report/Bingeling-report.pdf` has 33 pages. |
| 2026-10-22 | Replaced the virtual-display screenshots with captures from Lab Terminal (sonder). Added Q11 and Q12. | 13 PNG files in `screenshots/`. Q11 and Q12 run in `scripts/run-queries.sh`. |
| 2026-10-22 | Added formatter settings and ran `ruff`, `prettier`, and `shellcheck`. Added the source check. | `shellcheck` reports no findings. STE lint reports no hard violations. |
| 2026-10-22 | Applied the author's answers: IEEE references, 14-page report, no extras in the report. | `bash scripts/build-report.sh` builds a 14-page PDF. |
| 2026-10-30 | Rewrote the case-study report and kept the original PDF. | Built `report/Bingeling-revised.pdf`. MongoDB counts matched the seed. Nine queries matched saved output exactly. Q8 had the same qualifying group with a different episode-array order. |
| 2026-10-30 | Replaced the old report with the revised report at the canonical path. Removed the alternate build and duplicate output. | `bash scripts/build-report.sh` built the final PDF with a cover on page 1. |
