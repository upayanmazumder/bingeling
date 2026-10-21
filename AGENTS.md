# Repository Guidelines

## Project Overview

Bingeling is a CSE302L Database Systems case study. It models a video streaming service with MongoDB. The assignment needs five simple queries, five complex queries, a report, screenshots, and a live demonstration. This repository is currently a documentation-first bootstrap. Seed scripts, data, queries, and tests do not exist yet.

## Architecture & Data Flow

- `docs/data-model.md` defines the planned `bingeling` database: `users`, `titles`, `watch_events`, `reviews`, and `plans`.
- Embed bounded, related data: profiles and current subscription in `users`, and cast, genres, seasons, and episodes in `titles`.
- Reference growing data: `watch_events` links `userId` and `titleId`. `reviews` links users and titles. `watch_events.titleName` duplicates the title name for reads, so renames need care.
- Planned flow: a script in `scripts/` generates JSON arrays in `data/`. Load those arrays into MongoDB, then run independent `queries/**/*.js` files with `mongosh`. Capture command output in `screenshots/` for the report. No loader or query file exists yet.
- The MongoDB container mounts the repository read-only at `/workspace`. Put generated repository files on the host, not inside that mount.

## Key Directories

- `docs/`: sourced domain analysis, collection model, fixed questions, and report outline.
- `scripts/` and `data/`: planned deterministic generator and `data/<collection>.json` arrays. Both contain only `.gitkeep` now.
- `queries/simple/` and `queries/complex/`: planned standalone query files. Both contain only `.gitkeep` now.
- `screenshots/`: planned command-and-output images for the report. It contains only `.gitkeep` now.

## Development Commands

```sh
docker compose up -d
docker compose exec mongo mongosh bingeling
```

`docker-compose.yml` starts MongoDB 7 on port 27017. After query files exist, run one from the repository root with `mongosh bingeling queries/simple/q01-thrillers-after-2018.js`. Alternatively, run it inside the container with `docker compose exec mongo mongosh bingeling queries/simple/q01-thrillers-after-2018.js`. No build, lint, test, or seed command exists yet. Do not describe planned query commands as passing checks.

## Code Conventions & Common Patterns

- Follow `GUIDELINES.md` for all new work. Write documents in Simplified Technical English with short, active sentences.
- Use plural collection names. Fields use camelCase, such as `releaseYear`, `runtimeMin`, `startedAt`, and `priceInr`. The collection `watch_events` uses snake_case.
- Movies use `runtimeMin`. Series use `seasons[].episodes[]`. Use BSON dates for timestamps and ObjectId references where `docs/data-model.md` specifies them.
- Keep growing arrays out of user and title documents. The indexes in `docs/data-model.md` are plans, not existing database indexes.
- Generate only synthetic names and email addresses. Use a fixed random seed. Target about 500 titles, 2,000 users, 50,000 watch events, and 5,000 reviews.
- Name each query `qNN-<slug>.js` under the matching directory. Start it with the question, intent, and collections used. Print results with `printjson` or `.toArray()`.
- Keep simple questions to `find`, projection, sort, limit, `countDocuments`, or `distinct`. Use MongoDB aggregation for complex questions. See `docs/questions.md` for fixed questions and operators.
- No application error handling, async pattern, dependency injection, or state-management convention exists. Do not invent one before implementation.

## Important Files

- `README.md`: scope, assignment requirements, and quick start.
- `GUIDELINES.md`: writing, seed, query, screenshot, and demo rules.
- `docs/data-model.md`: document shapes, reference choices, and planned indexes.
- `docs/questions.md`: Q1–Q10 and planned paths. Treat these questions as fixed.
- `docs/domain-analysis.md`: sourced research and limitations.
- `docs/report-outline.md`: required submission structure.
- `docker-compose.yml`: MongoDB service and read-only repository mount.

## Runtime/Tooling Preferences

- Use Docker Compose and MongoDB 7. Query files use `mongosh` JavaScript and database `bingeling`.
- The repository does not choose Node, Bun, Python, or a package manager for seed generation. `.gitignore` mentions Node and Python artifacts, but it does not select a runtime.
- Do not assume an application server, CI system, or package scripts exist.

## Testing & QA

- No test framework, test suite, CI workflow, or coverage target exists yet. Do not claim test coverage.
- Each future query must run alone and print visible results. Save `screenshots/qNN-<slug>.png` with both its command and output.
- Before review, test the complete flow from an empty database: start MongoDB, generate and load seed data, then run all ten queries. The seed and query steps remain unimplemented.
- Check that complex queries answer the fixed questions. Revenue and churn need historical billing records, which the current user subscription snapshot does not provide. Do not report historical values as measured without that data.
