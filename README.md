# Bingeling — CSE302L Database Systems Case Study

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
| `docs/questions.md` | The 5 simple and 5 complex questions and their query files |
| `docs/report-outline.md` | Structure of the final submission document |
| `GUIDELINES.md` | Rules for work in this repository |
| `docker-compose.yml` | Local MongoDB 7 instance |
| `data/` | Generated JSON arrays and a source manifest |
| `scripts/` | Data generation, loading, validation, query runner, and report build |
| `queries/simple/`, `queries/complex/` | One runnable `.js` file per question |
| `screenshots/` | Terminal screenshots of query execution |

## Quick start

Docker, Docker Compose, Bash, and Python 3 are required. The first run pulls MongoDB 7.
The demo removes only this Compose project's database volume before it loads the committed data.

```sh
bash scripts/demo.sh
bash scripts/build-report.sh
```

The final document is `report/Bingeling-report.pdf`. The build reads the ten
query files, saved outputs, seed arrays, and terminal screenshots.
To run one query after the demo:

```sh
docker compose exec -T mongo mongosh --quiet bingeling queries/simple/q01-thrillers-after-2018.js
```

To rebuild the data from original sources, run `python3 scripts/generate_data.py`.
See `docs/data-sources.md` for source terms and `docs/seed-design.md` for field provenance.

To regenerate the screenshots, load the data and start the "Lab Terminal (sonder)" app on Hyprland:

```sh
bash scripts/capture-lab-terminal.sh
```

The script opens one `mongosh` session in the MongoDB container. It runs each query there with `load()`.
It types into the real terminal window and captures only that window with `grim`.
It needs `hyprctl`, `wtype`, `grim`, and ImageMagick. Review each PNG in `screenshots/` before building the report.

Format code before a commit with `ruff format`, `ruff check`, `prettier --write`, and `shellcheck`.
The `.editorconfig`, `.prettierrc.json`, and `ruff.toml` files hold the settings.

## Status

The ten query files, generated data, and final report are part of this repository.

## Assignment requirements

1. Choose a domain — Entertainment (video streaming).
2. Implement the database with NoSQL — MongoDB.
3. Execute at least 10 queries.
4. Answer 5 simple questions with query execution.
5. Answer 5 complex questions with query execution.
6. Submit a document with domain analysis, question explanations, queries, and screenshots.
7. Be ready to run the queries live.
