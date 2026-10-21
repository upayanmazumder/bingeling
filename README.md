# StreamDB — CSE302L Database Systems Case Study

NoSQL case study for the **Entertainment** domain. The subject is a video streaming platform (similar to Netflix or Prime Video). The database is **MongoDB**.

## Why this domain

- The data is semi-structured. Titles have variable fields: movies have a runtime, series have seasons and episodes.
- The access patterns suit documents: a title page reads one document with embedded cast and genres.
- Watch events have high volume and append-only writes. This is a typical NoSQL workload.
- The data gives useful insights: popular genres, user retention, binge behaviour, and revenue by plan.

## Repository layout

| Path | Purpose |
|------|---------|
| `docs/domain-analysis.md` | Analysis of the streaming domain and stakeholders |
| `docs/data-model.md` | Collections, document shapes, indexes, design decisions |
| `docs/questions.md` | The 5 simple and 5 complex questions (queries to be written) |
| `docs/report-outline.md` | Structure of the final submission document |
| `GUIDELINES.md` | Rules for work in this repository |
| `docker-compose.yml` | Local MongoDB 7 instance |
| `data/` | Generated seed data (JSON) |
| `scripts/` | Seed and data generation scripts |
| `queries/simple/`, `queries/complex/` | One `.js` file per question, run with `mongosh` |
| `screenshots/` | Execution screenshots for the report |

## Quick start

```sh
docker compose up -d
docker compose exec mongo mongosh streamdb
```

## Status

Bootstrap only. The seed scripts and the queries are not implemented yet. See `docs/questions.md` for the list of work.

## Assignment requirements

1. Choose a domain — Entertainment (video streaming).
2. Implement the database with NoSQL — MongoDB.
3. Execute at least 10 queries.
4. Answer 5 simple questions with query execution.
5. Answer 5 complex questions with query execution.
6. Submit a document with domain analysis, question explanations, queries, and screenshots.
7. Be ready to run the queries live.
