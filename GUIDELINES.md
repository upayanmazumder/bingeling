# Guidelines

## Writing

- Use Simplified Technical English (ASD-STE100) in all documents.
- Keep sentences short. Use active voice. Use one term for one concept.

## Data

- Store seed data as JSON arrays in `data/<collection>.json`.
- Generate data with a script in `scripts/`. Use a fixed random seed so results are reproducible.
- Use realistic volumes: about 500 titles, 2,000 users, 50,000 watch events, 5,000 reviews.
- Do not commit real personal data. Use generated names and e-mail addresses.

## Queries

- Put each question in its own file: `queries/simple/q01-<slug>.js` to `queries/complex/q10-<slug>.js`.
- Start each file with a comment block: the question, the intent, and the collections used.
- Each file must run alone: `mongosh bingeling queries/simple/q01-<slug>.js`.
- Print results with `printjson` or `.toArray()` so the screenshot shows the output.
- Simple questions use `find`, projection, sort, limit, `countDocuments`, or `distinct`.
- Complex questions use the aggregation pipeline: `$lookup`, `$unwind`, `$group`, `$facet`, `$bucket`, window functions, or date operators.

## Screenshots

- Name each screenshot after its query file: `screenshots/q01-<slug>.png`.
- Show the command and the output in the same image.

## Live demo

- `docker compose up -d`, then run the seed script, then run any query file.
- Test the full flow from an empty database before the review.
