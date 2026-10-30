# Changelog

## Unreleased

### Changed
- Replaced the old report with the rewritten case study at `report/Bingeling-report.pdf`.
- The single build command produces the final report with ten queries, answers, and execution screenshots.

## 1.0.1 - 2026-10-22

### Changed
- The report uses IEEE numeric citations with access dates.
- The report fits in 14 pages: smaller margins and fonts, one-line sample documents, and no duplicate output blocks.
- The report does not include the extra queries Q11 and Q12. They stay in the repository.

## 1.0.0 - 2026-10-22

### Added
- Real-first MongoDB seed pipeline, data model, and provenance records.
- Ten standalone database queries and a full-flow runner.
- Two extra queries: index effect with `explain` (Q11) and text search (Q12).
- Empty-database demo script and GitHub Actions CI.
- Final report source, PDF build, and terminal screenshots from the Lab Terminal app.
- Formatter settings: `.editorconfig`, `.prettierrc.json`, and `ruff.toml`.
- Source check note with access dates in the domain analysis and the report references.

### Changed
- Docker Compose now waits for a healthy database.
- Queries run with the query file as a `mongosh` argument and read the manifest with `require('fs')`.
- The text index on `titles` uses `textLanguage` as its language override field.
- The repository has a description and topics. The merged local branch is deleted.
