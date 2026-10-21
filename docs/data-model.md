# Data Model

Database name: `bingeling`.

## Collections

### `users`
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string (unique)",
  "country": "IN",
  "joinedAt": "Date",
  "profiles": [{ "name": "string", "kids": false }],
  "subscription": { "plan": "basic|standard|premium", "status": "active|cancelled", "startedAt": "Date", "endedAt": "Date|null" }
}
```

### `titles`
```json
{
  "_id": "ObjectId",
  "type": "movie|series",
  "name": "string",
  "releaseYear": 2021,
  "language": "en",
  "genres": ["Drama", "Thriller"],
  "maturity": "U|UA|A",
  "cast": [{ "name": "string", "role": "string" }],
  "runtimeMin": 128,
  "seasons": [{ "number": 1, "episodes": [{ "number": 1, "name": "string", "runtimeMin": 45 }] }]
}
```
`runtimeMin` is for movies only. `seasons` is for series only.

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
  "completed": true
}
```

### `reviews`
```json
{ "_id": "ObjectId", "userId": "ObjectId", "titleId": "ObjectId", "rating": 4, "text": "string", "createdAt": "Date" }
```

### `plans`
```json
{ "_id": "premium", "priceInr": 649, "screens": 4, "maxQuality": "4K" }
```

## Indexes (planned)

| Collection | Index | Reason |
|------------|-------|--------|
| users | `{ email: 1 }` unique | Login lookup |
| titles | `{ genres: 1, releaseYear: -1 }` | Browse by genre |
| titles | text on `name`, `cast.name` | Search |
| watch_events | `{ userId: 1, startedAt: -1 }` | Continue watching |
| watch_events | `{ titleId: 1 }` | Title analytics |
| reviews | `{ titleId: 1, userId: 1 }` unique | One review per user per title |

## Embed or reference

| Relation | Choice | Reason |
|----------|--------|--------|
| Title → cast, genres, episodes | Embed | Bounded, always read together |
| User → subscription, profiles | Embed | Bounded, one owner |
| User → watch events | Reference | Unbounded growth |
| Title → reviews | Reference | Unbounded growth |
