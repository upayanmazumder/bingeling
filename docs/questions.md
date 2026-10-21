# Questions

Status: all ten fixed questions have standalone mongosh queries. Run each query from the repository root against the seeded `bingeling` database. Queries print counts and compact Extended JSON rows. Large results show a labeled sample. Q1 and Q5 show the first 10 rows. Q7 and Q9 show the first 20 rows. Q8 shows the top 25 rows.

## Simple (5)

| # | Question | Planned operators | File |
|---|----------|-------------------|------|
| Q1 | List all Thriller movies released after 2018, newest first. | `find`, sort | `queries/simple/q01-thrillers-after-2018.js` |
| Q2 | How many users have an active premium subscription? | `countDocuments` | `queries/simple/q02-active-premium-count.js` |
| Q3 | Which languages are in the catalogue? | `distinct` | `queries/simple/q03-catalogue-languages.js` |
| Q4 | Show the 10 most recent watch events of one user. | `find`, sort, limit, projection | `queries/simple/q04-recent-watches.js` |
| Q5 | Find titles that feature a given actor. | `find` on embedded array | `queries/simple/q05-titles-by-actor.js` |

## Complex (5)

| # | Question | Planned operators | File |
|---|----------|-------------------|------|
| Q6 | What are the top 5 genres by total watch minutes in each country? | `$lookup`, `$unwind`, `$group`, `$sort`, `$topN` | `queries/complex/q06-top-genres-by-country.js` |
| Q7 | What is the completion rate of each movie, with average rating? | `$group`, `$lookup` on reviews, `$project` | `queries/complex/q07-completion-vs-rating.js` |
| Q8 | Which users binge-watched (3 or more episodes of one series on one day)? | `$dateTrunc`, `$group`, `$match` | `queries/complex/q08-binge-watchers.js` |
| Q9 | What is the monthly revenue and churn per plan? | `$lookup` on plans, `$group` by month, `$facet` | `queries/complex/q09-revenue-and-churn.js` |
| Q10 | How does device usage change by hour of day? | `$hour`, `$bucket`, `$setWindowFields` | `queries/complex/q10-device-usage-by-hour.js` |

Q4 reads `demoUserId` (a 24-character ObjectId hex) from `data/manifest.json`. Q5 reads `demoActor` (an exact credited cast name) from the same file. Both use `require('fs')`.

Q8 uses each user's IANA `timezone` for local-day grouping. It counts distinct **completed** season and episode pairs.

Q9 reports UTC payment months with payments. It sums actual payment amounts. Churn is the number of users whose subscription ended with status `cancelled` in that month, divided by the subscribers active at the month's start. Churn is null when the denominator is zero.

Q10 uses each user's local hour. Its running share is the cumulative fraction of a device's events across hours 0 to 23. It is not a trend over calendar time.

## Extra queries

- Q11 compares a collection scan with the index scan for the Q4 lookup: `queries/extra/q11-explain-index.js`.
- Q12 searches title and cast names with the text index: `queries/extra/q12-text-search.js`.
