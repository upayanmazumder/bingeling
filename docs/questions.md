# Questions

Status: the questions are fixed. The queries are not written yet.

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

## Extra queries (optional)

- Text search on title and cast names.
- `explain("executionStats")` before and after an index, to show the index effect.
