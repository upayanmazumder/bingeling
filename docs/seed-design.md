# Seed Design

Run `python3 scripts/generate_data.py --download` from the repository root. The first run downloads two archives to ignored `data/raw/`. Later runs can omit `--download`. The script uses Python's standard library and fixed seed `367`. It writes six JSON arrays and `data/manifest.json`. Do not edit the arrays by hand. The generator checks the pinned Netflix archive checksum and records both archive checksums. The manifest records checksums for generated arrays.

Run `docker compose up -d` and `scripts/load.sh` to replace the six Bingeling collections. The loader imports Extended JSON with `mongoimport --jsonArray --drop`. It then applies `scripts/schema.js`. Run `docker compose exec -T mongo mongosh --quiet bingeling scripts/validate.js` to check loaded counts, BSON types, references, demo anchors, and provenance. These actions require Docker Compose and a running MongoDB container. A load is repeatable on an empty database. A new load replaces only the six project collections.

## Records

| Collection | Count | Source and simulation |
|---|---:|---|
| `titles` | 500 | 400 linked Netflix movies and 100 Netflix series. The movie-to-IMDb ID comes from MovieLens links where present. Synthetic language, episode names, and episode runtimes are marked. |
| `users` | 2,000 | Anonymous MovieLens user IDs select the accounts. Names, reserved-domain email addresses, country, timezone, profiles, and subscription state are synthetic. |
| `watch_events` | 50,000 | 49,997 events use anonymous MovieLens user and movie IDs plus real rating timestamps as proxies. All playback fields are synthetic. Three completed episode events form the labelled synthetic binge case. |
| `reviews` | 5,000 | Distinct MovieLens user/movie ratings supply the score and rating timestamp. Text stays empty because the dataset has no review prose. |
| `plans` | 3 | Case-study prices in INR. These are examples, not an assertion about a provider's live pricing. |
| `payments` | 33,776 | Fully synthetic monthly invoices. `periodStart` is inclusive and `periodEnd` is exclusive. |

The generated event share is 49,997 / 50,000 = **99.994%** rating-backed
timestamp proxies. The remaining **0.006%** is the synthetic binge case.
All 5,000 review ratings and timestamps come from MovieLens.

The generator chooses popular matched films and then the 2,000 users with the most ratings on those films. It samples source rating rows without replacement. It stores source user and movie IDs for traceability. It does not copy tags or raw dataset files. This selection is not a random sample of platform viewers. The public datasets do not provide viewing, device, subscription, payment, or region data.

Each ObjectId has a two-digit hexadecimal collection code and a zero-padded numeric source ID or sequence. Users use `01`, titles `02`, watch events `03`, reviews `04`, and payments `05`. JSON uses Extended JSON `$oid` and `$date`, so `mongoimport` preserves BSON types. `data/manifest.json` contains `demoUserId`, `demoActor`, and `bingeTitleId`. Query Q4 uses the demo user. Q5 uses the credited actor. Q8 uses the completed three-episode series scenario, placed on one Asia/Kolkata calendar day. The validator checks all three anchors. All file counts, generated hashes, and real-versus-synthetic event totals remain in the manifest.

The demo metrics describe an artificial case study. Do not present watch duration, completion, geography, churn, revenue, or device usage as measured platform behavior. A rating timestamp is a proxy for an event start. It can predate the synthetic subscription start, since MovieLens has no Bingeling membership records. An invoice is a generated example rather than a historical charge.
