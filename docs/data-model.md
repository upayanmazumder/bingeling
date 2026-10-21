# Data Model

Database name: `bingeling`. The generated arrays use Extended JSON `$oid` and `$date`.

## Collections

### `users`
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string (unique)",
  "country": "IN",
  "timezone": "Asia/Kolkata",
  "joinedAt": "Date",
  "profiles": [{ "name": "string", "kids": false }],
  "subscription": { "plan": "basic|standard|premium", "status": "active|cancelled", "startedAt": "Date", "endedAt": "Date|null" }
}
```
`sourceUserId` is an anonymous MovieLens user ID. Names, email addresses,
countries, timezones, profiles, and subscription fields are synthetic.

### `titles`
```json
{
  "_id": "ObjectId",
  "type": "movie|series",
  "name": "string",
  "releaseYear": 2021,
  "productionCountries": ["India"],
  "language": "en",
  "genres": ["Drama", "Thriller"],
  "maturity": "U|UA|A",
  "cast": [{ "name": "string" }],
  "runtimeMin": 128,
  "seasons": [{ "number": 1, "episodes": [{ "number": 1, "name": "Episode 1", "runtimeMin": 45 }] }],
  "source": { "dataset": "netflix-shows-2021", "showId": "s123", "netflixRating": "TV-MA", "listedIn": "TV Dramas", "movieLensMovieId": 12, "imdbId": "tt0000001" }
}
```
`runtimeMin` is for movies only. `seasons` is for series only.
`source.showId` comes from the Netflix snapshot. Linked movies add
`source.movieLensMovieId` and, when present, `source.imdbId` from MovieLens links.
`languageOrigin` marks the country-based language proxy. `maturityOrigin`
marks the Netflix rating mapping. Series episodes carry `episodeOrigin`
because Netflix lists seasons but not episodes.

### `watch_events`
```json
{
  "_id": "ObjectId",
  "userId": "ObjectId",
  "titleId": "ObjectId",
  "titleName": "string (denormalised)",
  "season": 1, "episode": 3,
  "device": "tv|mobile|web|tablet",
  "startedAt": "Date",
  "minutesWatched": 42,
  "completed": true,
  "origin": "movielens-rating-proxy|synthetic|synthetic-binge-scenario"
}
```
`origin` identifies rating-timestamp proxies or synthetic sessions.
The source does not provide real viewing minutes, devices, or completion states.

### `reviews`
```json
{ "_id": "ObjectId", "userId": "ObjectId", "titleId": "ObjectId", "rating": 4.5, "text": "", "createdAt": "Date", "origin": "movielens-rating" }
```
Ratings and timestamps come from MovieLens. Empty `text` does not claim real review prose.

### `plans`
```json
{ "_id": "premium", "name": "premium", "priceInr": 649, "screens": 4, "maxQuality": "4K" }
```

### `payments`
```json
{ "_id": "ObjectId", "userId": "ObjectId", "plan": "premium", "amountInr": 649, "paidAt": "Date", "periodStart": "Date", "periodEnd": "Date", "origin": "synthetic" }
```
The billing period starts at `periodStart` and ends before `periodEnd`.
Payments and subscription states are case-study data, not real invoices.

## Indexes

| Collection | Index | Reason |
|------------|-------|--------|
| users | `{ email: 1 }` unique | Login lookup |
| titles | `{ genres: 1, releaseYear: -1 }` | Browse by genre |
| titles | text on `name`, `cast.name` | Search |
| watch_events | `{ userId: 1, startedAt: -1 }` | Continue watching |
| watch_events | `{ titleId: 1 }` | Title analytics |
| reviews | `{ titleId: 1, userId: 1 }` unique | One review per user per title |
| payments | `{ plan: 1, periodStart: 1 }` | Monthly revenue |
| payments | `{ userId: 1, periodStart: 1 }` unique | One payment per user per month |

`scripts/schema.js` installs these indexes and BSON validators after each import.
`scripts/validate.js` checks counts, references, BSON types, and query anchors.
See [source terms](data-sources.md) and [seed design](seed-design.md) for provenance.

## Embed or reference

| Relation | Choice | Reason |
|----------|--------|--------|
| Title → cast, genres, episodes | Embed | Bounded, always read together |
| User → subscription, profiles | Embed | Bounded, one owner |
| User → watch events | Reference | Unbounded growth |
| Title → reviews | Reference | Unbounded growth |
