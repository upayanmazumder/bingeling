# Live demo runbook

## Before the session

1. Install Docker Engine, Docker Compose, Bash, and Python 3.
2. Pull `mongo:7` while the network works.
3. Keep the committed `data/*.json`, `queries/`, and `screenshots/` available offline.
4. Read `data/manifest.json` for the demo user ID and actor.

## Run from an empty database

```sh
bash scripts/demo.sh
bash scripts/build-report.sh
```

The demo removes the database volume for this Compose project. It imports the six collections and validates the records. It runs all ten questions. It saves text outputs in `docs/query-output/`.

To repeat one query, run this command with any query path:

```sh
docker compose exec -T mongo mongosh --quiet bingeling queries/simple/q01-thrillers-after-2018.js
```

Use `docs/questions.md` for the complete query path list. Show the manifest, collection counts, then Q1, Q6, Q8, Q9, and Q10. Show the remaining questions if the examiner requests them.

## If a service fails

- Run `docker compose ps` to inspect the MongoDB health state.
- Run `docker compose logs mongo` to inspect MongoDB errors.
- Use the committed query outputs and terminal screenshots only as evidence of earlier runs. Do not claim that saved output is a live execution.
- If Docker is unavailable, show the PDF and the query source files. State that a live database is unavailable.

## Questions for the viva

1. **Why MongoDB?** A title document holds bounded cast, genres, and episode details. A title page reads them together.
2. **Why not one collection?** Watch events and reviews grow without a bound. Separate collections avoid large title and user documents.
3. **Why embed cast?** Cast changes rarely and belongs to a title page.
4. **Why reference events?** A user can produce many events. A reference keeps the user document bounded.
5. **Why duplicate `titleName`?** It makes recent viewing output simple. Renames can leave stale names.
6. **Why use indexes?** The genre and recent-viewing indexes match Q1 and Q4 filters and sorts.
7. **Are the users real?** User IDs originate from anonymous MovieLens records. Names and e-mail addresses are generated.
8. **Are watch events real?** Source ratings and timestamps are real. A rating is a proxy for a watch, not proof of viewing.
9. **Are billing figures real?** No. Payments are generated. Plan prices use cited public values.
10. **What is churn?** Cancelled accounts in a month divided by accounts active at the start of that month.
11. **Why distinct episodes in Q8?** Replaying one episode must not count as a binge.
12. **What does Q10 show?** It groups proxy times by device. The device is generated and the source times are not India watch times.
13. **What limits the catalogue?** The public title sources cover selected titles and years. This is not a complete service catalogue.
14. **How do you repeat results?** The generator fixes its selection seed, and the repo commits the JSON arrays.
