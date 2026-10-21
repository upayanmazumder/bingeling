# Findings and decisions

Record evidence before using a number in the report. `F` entries describe observations. `D` entries describe design choices.

| ID | Finding or decision | Evidence and effect |
|---|---|---|
| F-01 | The initial repository had no seed data, queries, or report. | The first full-flow run must start from an empty database. |
| F-02 | Q9 needs payment history. A current subscription alone cannot show monthly revenue. | The data model includes `payments`. |
| F-03 | Q6 needs multiple user countries. | The data model permits several country codes. |
| D-01 | Use MongoDB 7 through Docker Compose. | The host has no `mongosh` or `mongoimport`. |
| D-02 | Use real public data where available. Mark generated values. | See `docs/data-sources.md` and `docs/seed-design.md`. |
| D-03 | Monthly churn is cancellations during the month divided by active subscriptions at its start. | The denominator uses the `startedAt` and `endedAt` dates, not the current status alone. |
| D-04 | Keep growing events and reviews separate from user and title documents. | Avoid unbounded embedded arrays. |
| D-05 | A rating timestamp is not a measured watch time. | Q10 must state this limit even when it uses real timestamps. |
| F-04 | A text index on `titles` failed because the `language` field is a MongoDB language override. | `scripts/schema.js` sets `language_override: 'textLanguage'`. |
| F-05 | `mongosh` has no `cat()` function in script mode, and stdin mode prints prompts. | Queries use `require('fs')`. The runner passes the query file as an argument. |
| F-06 | Real sources: Netflix titles (Kaggle, CC0) and MovieLens 32M ratings (non-commercial research terms). | 400 movies, 100 series, 2,000 anonymous user IDs, 5,000 reviews, and 49,997 of 50,000 events use real records. |
| F-07 | MovieLens has no viewing, device, subscription, payment, or region data. | These fields are generated. Three synthetic events form the Q8 binge case. Payments are fully synthetic. |
| F-08 | The full flow from an empty volume takes about 22 seconds on the build host. | `bash scripts/demo.sh` loaded 6 collections, validated, and ran 10 queries. |
| F-09 | Q11 shows the index effect on the Q4 lookup. | The collection scan examined 50,000 documents. The index scan examined 10 documents and 10 keys. |
| F-10 | A source check on 22 October 2026 reached 25 of 29 cited URLs. | Four URLs returned HTTP 403 to an automated request. The author must read them. See `docs/domain-analysis.md`. |
| D-06 | Build the report as Markdown, then Typst, then PDF. | Typst is small and the build works in CI. The course template, citation style, and page limit are still unknown. |
| D-07 | Capture screenshots in the Lab Terminal app. One `mongosh` session runs every query with `load()`. | `scripts/capture-lab-terminal.sh` drives the real window with `wtype` and captures it with `grim`. |
