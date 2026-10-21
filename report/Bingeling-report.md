```{=typst}
#set heading(numbering: "1.")
#align(center)[
  #v(22%)
  #text(size: 30pt, weight: "bold")[Bingeling]
  #v(1cm)
  #text(size: 18pt)[MongoDB Video Streaming Case Study]
  #v(2cm)
  #text(size: 16pt)[24BDS0367 Upayan Mazumder]
  #v(1cm)
  #text(size: 12pt)[CSE302L Database Systems]
  #v(1cm)
  #text(size: 12pt)[22 October 2026]
]
#pagebreak()
#outline(title: [Contents])
#pagebreak()
```

# Introduction

Bingeling models a video streaming service with MongoDB 7. It stores catalogue titles, user subscriptions, rating-derived viewing proxies, reviews, plans, and generated payments. This course case study uses published catalogue and rating records where marked. It does not operate a real streaming service. The objective is to answer five simple and five complex database questions with reproducible queries and captured results [R1–R4].

# Domain analysis

Video services need catalogue discovery, viewing history, subscriber state, and billing records. Subscribers need recent sessions. Content teams need viewing measures by title and region. Finance needs dated payments and cancellations. Product teams need completion and device-use measures [R1].

Market figures have different definitions. The Government of India reported INR 9,200 crore in Indian video subscription revenue for 2024, citing FICCI-EY [R7]. FICCI-EY counted 216 million paid video subscriptions across 143 million households in 2025 [R6]. These are market context, not measurements of Bingeling. Netflix reported 96 billion viewing hours for July–December 2025. That figure covers Netflix, not this dataset [R5].

ZEE5 reported 105 billion watch minutes in FY25 and said connected devices supplied 64% of premium-content watch time. These figures describe ZEE5, not all Indian viewers [R14].

Streaming services can earn from subscriptions, ads, rentals, or combinations. This model covers subscriptions and simulated payments. Its watch events are rating-based viewing proxies or explicit synthetic scenarios, not observed video plays. It stores no video files or streaming bandwidth. The source distributions in [R1] describe IMDb metadata, not an Indian platform sample.

# Choice of database

MongoDB documents hold each title with its genres, cast, and bounded seasons. A title page can read these fields together. A user document holds a small profile list and the current subscription. MongoDB also supports aggregation pipelines for joins, time grouping, and ranking [R8]. SonyLIV reported improved content-management search after its move to MongoDB Atlas. That vendor case study concerns a content system. It does not prove that MongoDB serves video bytes [R10].

Reference the growing `watch_events`, `reviews`, and `payments` collections rather than embedding them in users or titles. Embedded unbounded histories would grow documents and could hit the 16 MB BSON limit [R9]. The copied `watch_events.titleName` aids display but becomes stale if a title changes name. Cross-document joins and updates cost work. A relational database could enforce more relationships with foreign keys. MongoDB is a fit for this course catalogue and event analysis, not a claim of universal superiority [R1, R2, R8].

# Data model

The database is `bingeling`. Each document uses `_id`. Referenced IDs are BSON `ObjectId` values in Extended JSON seed files. Timestamps are BSON dates encoded as Extended JSON `$date`. The six collections are:

| Collection | Role | Main relationships |
|---|---|---|
| `users` | Generated identities, country, current subscription | `_id` joins events, reviews, payments |
| `titles` | Movies and series, cast and catalogue metadata | `_id` joins events and reviews |
| `watch_events` | One generated viewing session per document | `userId`, `titleId`; copied `titleName` |
| `reviews` | Selected MovieLens rating records, with empty text | `userId`, `titleId` |
| `plans` | Plan price in INR | Plan key joins users and payments |
| `payments` | Generated billing period and paid amount | `userId`, plan key |

Movies have `runtimeMin`. Series have `seasons[].episodes[]` with episode runtimes. Events can identify a season and episode. Plans store `priceInr`; payment records store `amountInr`, `paidAt`, `periodStart`, and `periodEnd`. A payment is a generated record, not proof of a real transfer. The model embeds bounded title details and a user's current subscription. It references growing session, review, and payment histories [R2].

The loader runs `scripts/schema.js`, which installs schema validators and indexes after import. Its indexes include unique `users.email`, `titles` by genre and release year, text search over title and cast names, `watch_events` by user and start time and by title, unique `(titleId, userId)` reviews, and payment indexes by plan or user and period start. These index definitions support the access patterns; this report does not claim measured speedups.

## Sample seed documents

The following examples come directly from the JSON arrays. The examples show stored types and field names, not a separate hand-written schema.

### `users`

```json
{
  "_id": {
    "$oid": "01000000000000000000001c"
  },
  "sourceUserId": 28,
  "name": "Meera Singh",
  "email": "bingeling-000028@example.com",
  "country": "IN",
  "timezone": "Asia/Kolkata",
  "joinedAt": {
    "$date": "1990-01-01T00:00:00Z"
  },
  "profiles": [
    {
      "name": "Main",
      "kids": false
    }
  ],
  "subscription": {
    "plan": "standard",
    "status": "active",
    "startedAt": {
      "$date": "2025-05-01T00:00:00Z"
    },
    "endedAt": null
  },
  "identityOrigin": "synthetic; sourceUserId is anonymous MovieLens ID"
}
```

### `titles`

```json
{
  "_id": {
    "$oid": "0200000000000000000009a8"
  },
  "type": "movie",
  "name": "Uncut Gems",
  "releaseYear": 2019,
  "productionCountries": [
    "United States"
  ],
  "language": "en",
  "languageOrigin": "synthetic-country-proxy",
  "genres": [
    "Drama",
    "Thriller"
  ],
  "maturity": "A",
  "maturityOrigin": "mapped-netflix-rating",
  "cast": [
    {
      "name": "Adam Sandler"
    },
    {
      "name": "LaKeith Stanfield"
    },
    {
      "name": "Kevin Garnett"
    },
    {
      "name": "Julia Fox"
    },
    {
      "name": "Idina Menzel"
    },
    {
      "name": "Eric Bogosian"
    },
    {
      "name": "Judd Hirsch"
    },
    {
      "name": "Abel Tesfaye"
    }
  ],
  "source": {
    "dataset": "netflix-shows-2021",
    "showId": "s2472",
    "netflixRating": "R",
    "listedIn": "Dramas, Thrillers",
    "movieLensMovieId": 209965,
    "imdbId": "tt5727208"
  },
  "runtimeMin": 135
}
```

### `watch_events`

```json
{
  "_id": {
    "$oid": "030000000000000000000001"
  },
  "userId": {
    "$oid": "01000000000000000000571d"
  },
  "titleId": {
    "$oid": "0200000000000000000000c0"
  },
  "titleName": "Wind River",
  "device": "web",
  "startedAt": {
    "$date": "2021-03-25T00:04:23Z"
  },
  "minutesWatched": 107,
  "completed": true,
  "origin": "movielens-rating-proxy",
  "sourceMovieId": 175569,
  "sourceRating": 3.5
}
```

### `reviews`

```json
{
  "_id": {
    "$oid": "040000000000000000000001"
  },
  "userId": {
    "$oid": "01000000000000000000571d"
  },
  "titleId": {
    "$oid": "0200000000000000000000c0"
  },
  "rating": 3.5,
  "text": "",
  "createdAt": {
    "$date": "2021-03-25T00:04:23Z"
  },
  "origin": "movielens-rating",
  "sourceMovieId": 175569
}
```

### `plans`

```json
{
  "_id": "basic",
  "name": "basic",
  "priceInr": 199,
  "screens": 1,
  "maxQuality": "HD"
}
```

### `payments`

```json
{
  "_id": {
    "$oid": "050000000000000000000001"
  },
  "userId": {
    "$oid": "01000000000000000000001c"
  },
  "plan": "standard",
  "amountInr": 499,
  "paidAt": {
    "$date": "2025-05-01T00:00:00Z"
  },
  "periodStart": {
    "$date": "2025-05-01T00:00:00Z"
  },
  "periodEnd": {
    "$date": "2025-06-01T00:00:00Z"
  },
  "origin": "synthetic"
}
```

# Data population

The checked-in arrays contain the following actual record counts at report-build time. Counts come from `data/<collection>.json`; they are not market estimates.

| Collection | Records |
|---|---:|
| `users` | 2,000 |
| `titles` | 500 |
| `watch_events` | 50,000 |
| `reviews` | 5,000 |
| `plans` | 3 |
| `payments` | 33,776 |

| Source archive | SHA-256 from manifest |
|---|---|
| `ml-32m.zip` | `e4a68655d7386b8f95f2f2424b2ff975dfdd15ffd59e0d864a14dca43e99d6ee` |
| `netflix-shows.zip` | `1e5477bbbe868845be3b852d80eec2f1da6570340860668549a6dd5da0b00054` |

The generator in `scripts/generate_data.py` uses fixed seed `367`. It selects 400 Netflix-listed movies matched to MovieLens links and 100 Netflix-listed series. The source archives and SHA-256 values are in `data/manifest.json`. The loader imports the Extended JSON arrays and applies validators and indexes. MovieLens anonymous rating IDs link synthetic user names to selected title ratings. Review scores and timestamps come from MovieLens, while review text is empty. Many watch-event timestamps come from those ratings and are **not** observed watch starts. The script converts rating at least 3 into `completed` and a full movie runtime. It converts a lower rating into a half-runtime session. Other events, series episodes, languages inferred from country, devices, subscriptions, and payments are generated. Actor names and catalogue labels come from Netflix metadata [R11–R13].

The Netflix titles source is a September 2021 CC0 snapshot [R13]. MovieLens 32M was generated in October 2023. It includes anonymous ratings, not demographics or watch logs [R12]. GroupLens permits research use and transformed redistribution only under its stated terms. It requires attribution and prohibits commercial or revenue-bearing use without permission. Those terms also apply to this derived seed data. This report does not imply GroupLens or University of Minnesota endorsement [R12, R15].

Title source labels: `netflix-shows-2021`: 500. Watch-event origin labels: `movielens-rating-proxy`: 49,997, `synthetic-binge-scenario`: 3. The source archives are not an up-to-date full platform inventory. Neither a MovieLens rating nor a linked user ID proves that anyone watched a title on Bingeling.

The fixed demo user has ObjectId `01000000000000000000001c`. The fixed demo actor is `Adam Sandler`. These values are selection anchors, not real customer identities. The population screenshot below shows a captured terminal count command and its result.

![Population command and database counts](../screenshots/population.png){ width=90% }

# Simple questions

For every question, the JavaScript block below is copied directly from the named query file at build time. The terminal excerpt comes from the saved output. The PNG is a captured command-and-output image. The full saved output is in `docs/query-output/`. No query result is simulated in this report.

## Q1: List all Thriller movies released after 2018, newest first.

**Explanation.** Filter the movie catalogue by genre and release year. Sort newer releases first.

**Query source:** `queries/simple/q01-thrillers-after-2018.js`

```javascript
// Q1: List all Thriller movies released after 2018, newest first.
// Intent: Filter the catalogue by type, genre and release year.
// Collections: titles.
const filter = { type: 'movie', genres: 'Thriller', releaseYear: { $gt: 2018 } };
printjson({ totalMatches: db.titles.countDocuments(filter), showingNewest: 10 });
db.titles.find(
  filter,
  { name: 1, releaseYear: 1, genres: 1, language: 1 }
).sort({ releaseYear: -1, name: 1 }).limit(10).forEach(row => printjson(EJSON.stringify(row)));
```

**Saved terminal output:** `docs/query-output/q01-thrillers-after-2018.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/simple/q01-thrillers-after-2018.js
{
  totalMatches: 10,
  showingNewest: 10
}
{"_id":{"$oid":"020000000000000000000380"},"name":"Oxygen","releaseYear":2021,"language":"en","genres":["Drama","International","Thriller"]}
{"_id":{"$oid":"0200000000000000000003e8"},"name":"Stowaway","releaseYear":2021,"language":"en","genres":["Drama","International","Thriller"]}
{"_id":{"$oid":"0200000000000000000007f5"},"name":"#Alive","releaseYear":2020,"language":"ko","genres":["Horror","International","Thriller"]}
{"_id":{"$oid":"0200000000000000000007cc"},"name":"The Devil All The Time","releaseYear":2020,"language":"en","genres":["Drama","Thriller"]}
{"_id":{"$oid":"020000000000000000000d65"},"name":"El Camino: A Breaking Bad Movie","releaseYear":2019,"language":"en","genres":["Drama","Thriller"]}
{"_id":{"$oid":"020000000000000000000d66"},"name":"Fractured","releaseYear":2019,"language":"en","genres":["Thriller"]}
{"_id":{"$oid":"020000000000000000000eb5"},"name":"I Am Mother","releaseYear":2019,"language":"en","genres":["International","Sci-Fi","Thriller"]}
{"_id":{"$oid":"020000000000000000000d9d"},"name":"In the Shadow of the Moon","releaseYear":2019,"language":"en","genres":["Drama","Sci-Fi","Thriller"]}
{"_id":{"$oid":"0200000000000000000009a8"},"name":"Uncut Gems","releaseYear":2019,"language":"en","genres":["Drama","Thriller"]}
{"_id":{"$oid":"020000000000000000001033"},"name":"Velvet Buzzsaw","releaseYear":2019,"language":"en","genres":["Drama","Thriller"]}
```

![Q1 captured command and output](../screenshots/q01-thrillers-after-2018.png){ width=90% }

**Insight and scope.** The generator intentionally selects recent linked Thrillers. Their presence is not proof of demand or an unbiased catalogue sample. The saved output and screenshot above contain the observed records.

## Q2: How many users have an active premium subscription?

**Explanation.** Count the users whose current plan is premium and whose current status is active.

**Query source:** `queries/simple/q02-active-premium-count.js`

```javascript
// Q2: How many users have an active premium subscription?
// Intent: Count users whose subscription is both premium and active.
// Collections: users.
printjson({ activePremiumUsers: db.users.countDocuments({
  'subscription.plan': 'premium',
  'subscription.status': 'active'
}) });
```

**Saved terminal output:** `docs/query-output/q02-active-premium-count.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/simple/q02-active-premium-count.js
{
  activePremiumUsers: 619
}
```

![Q2 captured command and output](../screenshots/q02-active-premium-count.png){ width=90% }

**Insight and scope.** The generator assigns each user a plan and status. This count measures the current synthetic snapshot, not subscriber growth. The saved output and screenshot above contain the observed records.

## Q3: Which languages are in the catalogue?

**Explanation.** List distinct language codes stored on title documents.

**Query source:** `queries/simple/q03-catalogue-languages.js`

```javascript
// Q3: Which languages are in the catalogue?
// Intent: List unique title languages alphabetically.
// Collections: titles.
printjson(db.titles.distinct('language').sort());
```

**Saved terminal output:** `docs/query-output/q03-catalogue-languages.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/simple/q03-catalogue-languages.js
[
  'en',
  'es',
  'hi',
  'ja',
  'ko'
]
```

![Q3 captured command and output](../screenshots/q03-catalogue-languages.png){ width=90% }

**Insight and scope.** The generator infers language from catalogue country. These codes are proxies, not confirmed audio-track languages or viewing shares. The saved output and screenshot above contain the observed records.

## Q4: Show the 10 most recent watch events of one user.

**Explanation.** Use the fixed demo user from the manifest. Sort that user's events by start time and limit the result to ten.

**Query source:** `queries/simple/q04-recent-watches.js`

```javascript
// Q4: Show the 10 most recent watch events of one user.
// Intent: Use the fixed demo user anchor and present their latest activity.
// Collections: watch_events; anchor from data/manifest.json.
const demoUserId = ObjectId(JSON.parse(require('fs').readFileSync('data/manifest.json', 'utf8')).demoUserId);
printjson({ userId: demoUserId, showingNewest: 10 });
db.watch_events.find(
  { userId: demoUserId },
  { titleName: 1, titleId: 1, startedAt: 1, minutesWatched: 1, completed: 1, device: 1, season: 1, episode: 1, origin: 1 }
).sort({ startedAt: -1, _id: -1 }).limit(10).forEach(row => printjson(EJSON.stringify(row)));
```

**Saved terminal output:** `docs/query-output/q04-recent-watches.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/simple/q04-recent-watches.js
{
  userId: ObjectId('01000000000000000000001c'),
  showingNewest: 10
}
{"_id":{"$oid":"03000000000000000000c350"},"titleId":{"$oid":"020000000000000000000002"},"titleName":"Blood & Water","season":1,"episode":3,"device":"tv","startedAt":{"$date":"2023-06-12T17:00:00Z"},"minutesWatched":52,"completed":true,"origin":"synthetic-binge-scenario"}
{"_id":{"$oid":"03000000000000000000c34f"},"titleId":{"$oid":"020000000000000000000002"},"titleName":"Blood & Water","season":1,"episode":2,"device":"tv","startedAt":{"$date":"2023-06-12T16:00:00Z"},"minutesWatched":46,"completed":true,"origin":"synthetic-binge-scenario"}
{"_id":{"$oid":"03000000000000000000c34e"},"titleId":{"$oid":"020000000000000000000002"},"titleName":"Blood & Water","season":1,"episode":1,"device":"tv","startedAt":{"$date":"2023-06-12T15:00:00Z"},"minutesWatched":31,"completed":true,"origin":"synthetic-binge-scenario"}
{"_id":{"$oid":"030000000000000000003323"},"titleId":{"$oid":"02000000000000000000040a"},"titleName":"Rush","device":"mobile","startedAt":{"$date":"2020-04-18T20:17:18Z"},"minutesWatched":123,"completed":true,"origin":"movielens-rating-proxy"}
{"_id":{"$oid":"030000000000000000004df3"},"titleId":{"$oid":"0200000000000000000005ce"},"titleName":"Rango","device":"tv","startedAt":{"$date":"2017-11-24T15:06:34Z"},"minutesWatched":110,"completed":true,"origin":"movielens-rating-proxy"}
{"_id":{"$oid":"030000000000000000007586"},"titleId":{"$oid":"020000000000000000001f19"},"titleName":"Scott Pilgrim vs. the World","device":"web","startedAt":{"$date":"2010-08-16T15:50:14Z"},"minutesWatched":112,"completed":true,"origin":"movielens-rating-proxy"}
{"_id":{"$oid":"03000000000000000000bac9"},"titleId":{"$oid":"020000000000000000002265"},"titleName":"Zombieland","device":"tablet","startedAt":{"$date":"2010-05-16T02:36:07Z"},"minutesWatched":88,"completed":true,"origin":"movielens-rating-proxy"}
{"_id":{"$oid":"030000000000000000000a67"},"titleId":{"$oid":"020000000000000000001e82"},"titleName":"Quantum of Solace","device":"mobile","startedAt":{"$date":"2010-05-16T02:33:38Z"},"minutesWatched":106,"completed":true,"origin":"movielens-rating-proxy"}
{"_id":{"$oid":"03000000000000000000a50c"},"titleId":{"$oid":"02000000000000000000023e"},"titleName":"Kung Fu Panda","device":"tv","startedAt":{"$date":"2010-05-16T02:32:28Z"},"minutesWatched":94,"completed":true,"origin":"movielens-rating-proxy"}
{"_id":{"$oid":"03000000000000000000ba1b"},"titleId":{"$oid":"020000000000000000001ae9"},"titleName":"Gran Torino","device":"web","startedAt":{"$date":"2009-12-27T18:19:53Z"},"minutesWatched":117,"completed":true,"origin":"movielens-rating-proxy"}
```

![Q4 captured command and output](../screenshots/q04-recent-watches.png){ width=90% }

**Insight and scope.** Many recorded start times are MovieLens rating times, not watched-at times. The result demonstrates sorting, not true recent viewing. The saved output and screenshot above contain the observed records.

## Q5: Find titles that feature a given actor.

**Explanation.** Use the fixed demo actor from the manifest. Match the name in each title's embedded cast.

**Query source:** `queries/simple/q05-titles-by-actor.js`

```javascript
// Q5: Find titles that feature a given actor.
// Intent: Match an actual credited actor against the embedded cast array.
// Collections: titles; actor anchor from data/manifest.json.
const demoActor = JSON.parse(require('fs').readFileSync('data/manifest.json', 'utf8')).demoActor;
const filter = { cast: { $elemMatch: { name: demoActor } } };
printjson({ actor: demoActor, totalMatches: db.titles.countDocuments(filter), showingFirst: 10 });
db.titles.find(
  filter,
  { name: 1, type: 1, releaseYear: 1, cast: 1 }
).sort({ name: 1 }).limit(10).forEach(row => printjson(EJSON.stringify(row)));
```

**Saved terminal output:** `docs/query-output/q05-titles-by-actor.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/simple/q05-titles-by-actor.js
{
  actor: 'Adam Sandler',
  totalMatches: 9,
  showingFirst: 10
}
{"_id":{"$oid":"020000000000000000001783"},"type":"movie","name":"50 First Dates","releaseYear":2004,"cast":[{"name":"Adam Sandler"},{"name":"Drew Barrymore"},{"name":"Rob Schneider"},{"name":"Sean Astin"},{"name":"Lusia Strus"},{"name":"Dan Aykroyd"},{"name":"Amy Hill"},{"name":"Allen Covert"},{"name":"Blake Clark"},{"name":"Maya Rudolph"}]}
{"_id":{"$oid":"020000000000000000001815"},"type":"movie","name":"Anger Management","releaseYear":2003,"cast":[{"name":"Adam Sandler"},{"name":"Jack Nicholson"},{"name":"Marisa Tomei"},{"name":"Luis Guzmán"},{"name":"Allen Covert"},{"name":"Lynne Thigpen"},{"name":"Kurt Fuller"},{"name":"Jonathan Loughran"},{"name":"Krista Allen"},{"name":"January Jones"},{"name":"Woody Harrelson"},{"name":"John Turturro"},{"name":"Kevin Nealon"}]}
{"_id":{"$oid":"0200000000000000000018a0"},"type":"movie","name":"Big Daddy","releaseYear":1999,"cast":[{"name":"Adam Sandler"},{"name":"Joey Lauren Adams"},{"name":"Jon Stewart"},{"name":"Cole Sprouse"},{"name":"Dylan Sprouse"},{"name":"Josh Mostel"},{"name":"Leslie Mann"},{"name":"Allen Covert"},{"name":"Rob Schneider"},{"name":"Kristy Swanson"}]}
{"_id":{"$oid":"020000000000000000001962"},"type":"movie","name":"Click","releaseYear":2006,"cast":[{"name":"Adam Sandler"},{"name":"Kate Beckinsale"},{"name":"Christopher Walken"},{"name":"David Hasselhoff"},{"name":"Henry Winkler"},{"name":"Julie Kavner"},{"name":"Sean Astin"},{"name":"Joseph Castanon"},{"name":"Jonah Hill"},{"name":"Jake Hoffman"},{"name":"Jennifer Coolidge"}]}
{"_id":{"$oid":"02000000000000000000001c"},"type":"movie","name":"Grown Ups","releaseYear":2010,"cast":[{"name":"Adam Sandler"},{"name":"Kevin James"},{"name":"Chris Rock"},{"name":"David Spade"},{"name":"Rob Schneider"},{"name":"Salma Hayek"},{"name":"Maria Bello"},{"name":"Maya Rudolph"},{"name":"Colin Quinn"},{"name":"Tim Meadows"},{"name":"Joyce Van Patten"}]}
{"_id":{"$oid":"020000000000000000001c95"},"type":"movie","name":"Little Nicky","releaseYear":2000,"cast":[{"name":"Adam Sandler"},{"name":"Patricia Arquette"},{"name":"Harvey Keitel"},{"name":"Rhys Ifans"},{"name":"Allen Covert"},{"name":"Tommy 'Tiny' Lister"},{"name":"Kevin Nealon"},{"name":"Jon Lovitz"},{"name":"Michael McKean"},{"name":"Quentin Tarantino"}]}
{"_id":{"$oid":"020000000000000000001d5e"},"type":"movie","name":"Mr. Deeds","releaseYear":2002,"cast":[{"name":"Adam Sandler"},{"name":"Winona Ryder"},{"name":"Peter Gallagher"},{"name":"Jared Harris"},{"name":"Allen Covert"},{"name":"Erick Avari"},{"name":"John Turturro"},{"name":"Peter Dante"},{"name":"Conchata Ferrell"},{"name":"Steve Buscemi"}]}
{"_id":{"$oid":"0200000000000000000009a8"},"type":"movie","name":"Uncut Gems","releaseYear":2019,"cast":[{"name":"Adam Sandler"},{"name":"LaKeith Stanfield"},{"name":"Kevin Garnett"},{"name":"Julia Fox"},{"name":"Idina Menzel"},{"name":"Eric Bogosian"},{"name":"Judd Hirsch"},{"name":"Abel Tesfaye"}]}
{"_id":{"$oid":"020000000000000000002257"},"type":"movie","name":"You Don't Mess with the Zohan","releaseYear":2008,"cast":[{"name":"Adam Sandler"},{"name":"John Turturro"},{"name":"Emmanuelle Chriqui"},{"name":"Nick Swardson"},{"name":"Lainie Kazan"},{"name":"Ido Mosseri"},{"name":"Rob Schneider"},{"name":"Dave Matthews"},{"name":"Michael Buffer"},{"name":"Charlotte Rae"}]}
```

![Q5 captured command and output](../screenshots/q05-titles-by-actor.png){ width=90% }

**Insight and scope.** This result checks a cast-based browse operation, not the actor's popularity. The saved output and screenshot above contain the observed records.

# Complex questions

For every question, the JavaScript block below is copied directly from the named query file at build time. The terminal excerpt comes from the saved output. The PNG is a captured command-and-output image. The full saved output is in `docs/query-output/`. No query result is simulated in this report.

## Q6: What are the top 5 genres by total watch minutes in each country?

**Explanation.** Join watch events to titles and users. Group watch minutes by country and genre, then rank genres within each country.

**Query source:** `queries/complex/q06-top-genres-by-country.js`

```javascript
// Q6: What are the top 5 genres by total watch minutes in each country?
// Intent: Attribute each watch's minutes to every genre of its title and rank within country.
// Collections: watch_events, users, titles.
const countries = db.watch_events.aggregate([
  { $lookup: { from: 'users', localField: 'userId', foreignField: '_id', as: 'user' } },
  { $unwind: '$user' },
  { $lookup: { from: 'titles', localField: 'titleId', foreignField: '_id', as: 'title' } },
  { $unwind: '$title' },
  { $unwind: '$title.genres' },
  { $group: {
    _id: { country: '$user.country', genre: '$title.genres' },
    totalMinutes: { $sum: '$minutesWatched' },
    watchEvents: { $sum: 1 }
  } },
  { $group: {
    _id: '$_id.country',
    topGenres: { $topN: {
      n: 5,
      sortBy: { totalMinutes: -1, '_id.genre': 1 },
      output: { genre: '$_id.genre', totalMinutes: '$totalMinutes', watchEvents: '$watchEvents' }
    } }
  } },
  { $project: { _id: 0, country: '$_id', topGenres: 1 } },
  { $sort: { country: 1 } }
]).toArray();
printjson({ countries: countries.length, genresPerCountry: 5 });
countries.forEach(row => printjson(EJSON.stringify(row)));
```

**Saved terminal output:** `docs/query-output/q06-top-genres-by-country.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/complex/q06-top-genres-by-country.js
{
  countries: 4,
  genresPerCountry: 5
}
{"topGenres":[{"genre":"Drama","totalMinutes":580075,"watchEvents":4897},{"genre":"Action","totalMinutes":513244,"watchEvents":4988},{"genre":"Comedy","totalMinutes":440062,"watchEvents":4885},{"genre":"Sci-Fi","totalMinutes":211244,"watchEvents":2193},{"genre":"Classic","totalMinutes":201907,"watchEvents":1687}],"country":"CA"}
{"topGenres":[{"genre":"Drama","totalMinutes":569915,"watchEvents":4860},{"genre":"Action","totalMinutes":504370,"watchEvents":4964},{"genre":"Comedy","totalMinutes":428851,"watchEvents":4785},{"genre":"Sci-Fi","totalMinutes":207042,"watchEvents":2164},{"genre":"Classic","totalMinutes":201454,"watchEvents":1708}],"country":"GB"}
{"topGenres":[{"genre":"Drama","totalMinutes":537635,"watchEvents":4552},{"genre":"Action","totalMinutes":462402,"watchEvents":4503},{"genre":"Comedy","totalMinutes":394917,"watchEvents":4370},{"genre":"Classic","totalMinutes":195290,"watchEvents":1600},{"genre":"Sci-Fi","totalMinutes":188585,"watchEvents":1975}],"country":"IN"}
{"topGenres":[{"genre":"Drama","totalMinutes":537669,"watchEvents":4548},{"genre":"Action","totalMinutes":463253,"watchEvents":4506},{"genre":"Comedy","totalMinutes":402808,"watchEvents":4479},{"genre":"Sci-Fi","totalMinutes":188076,"watchEvents":1944},{"genre":"Classic","totalMinutes":184411,"watchEvents":1532}],"country":"US"}
```

![Q6 captured command and output](../screenshots/q06-top-genres-by-country.png){ width=90% }

**Insight and scope.** Countries are assigned to anonymous rating IDs. Multi-genre titles add their minutes to each genre, so genre totals overlap. The saved output and screenshot above contain the observed records.

## Q7: What is the completion rate of each movie, with average rating?

**Explanation.** For each movie, aggregate its watch events and independently average its reviews. An unwatched movie has no completion percentage.

**Query source:** `queries/complex/q07-completion-vs-rating.js`

```javascript
// Q7: What is the completion rate of each movie, with average rating?
// Intent: Count completed movie watches and independently average title reviews (no fan-out).
// Collections: titles, watch_events, reviews.
const movies = db.titles.aggregate([
  { $match: { type: 'movie' } },
  { $lookup: {
    from: 'watch_events', let: { titleId: '$_id' },
    pipeline: [
      { $match: { $expr: { $eq: ['$titleId', '$$titleId'] } } },
      { $group: {
        _id: null,
        watches: { $sum: 1 },
        completedWatches: { $sum: { $cond: ['$completed', 1, 0] } }
      } }
    ], as: 'watchStats'
  } },
  { $lookup: {
    from: 'reviews', let: { titleId: '$_id' },
    pipeline: [
      { $match: { $expr: { $eq: ['$titleId', '$$titleId'] } } },
      { $group: { _id: null, averageRating: { $avg: '$rating' }, reviewCount: { $sum: 1 } } }
    ], as: 'reviewStats'
  } },
  { $set: {
    watchStats: { $first: '$watchStats' },
    reviewStats: { $first: '$reviewStats' }
  } },
  { $project: {
    _id: 0, title: '$name', releaseYear: 1,
    watches: { $ifNull: ['$watchStats.watches', 0] },
    completedWatches: { $ifNull: ['$watchStats.completedWatches', 0] },
    completionRatePct: {
      $cond: [
        { $gt: ['$watchStats.watches', 0] },
        { $round: [{ $multiply: [{ $divide: ['$watchStats.completedWatches', '$watchStats.watches'] }, 100] }, 2] },
        null
      ]
    },
    reviewCount: { $ifNull: ['$reviewStats.reviewCount', 0] },
    averageRating: { $round: ['$reviewStats.averageRating', 2] }
  } },
  { $sort: { completionRatePct: -1, title: 1 } }
]).toArray();
printjson({ totalMovies: movies.length, showingFirst: Math.min(20, movies.length) });
movies.slice(0, 20).forEach(row => printjson(EJSON.stringify(row)));
```

**Saved terminal output:** `docs/query-output/q07-completion-vs-rating.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/complex/q07-completion-vs-rating.js
{
  totalMovies: 400,
  showingFirst: 20
}
{"releaseYear":2011,"title":"Jiro Dreams of Sushi","watches":55,"completedWatches":54,"completionRatePct":98.18,"reviewCount":1,"averageRating":4.5}
{"releaseYear":2019,"title":"Klaus","watches":30,"completedWatches":29,"completionRatePct":96.67,"reviewCount":1,"averageRating":4}
{"releaseYear":2010,"title":"Senna","watches":54,"completedWatches":52,"completionRatePct":96.3,"reviewCount":6,"averageRating":3.67}
{"releaseYear":1969,"title":"True Grit","watches":44,"completedWatches":42,"completionRatePct":95.45,"reviewCount":7,"averageRating":3.57}
{"releaseYear":2015,"title":"Spotlight","watches":131,"completedWatches":125,"completionRatePct":95.42,"reviewCount":6,"averageRating":4}
{"releaseYear":2019,"title":"El Camino: A Breaking Bad Movie","watches":43,"completedWatches":41,"completionRatePct":95.35,"reviewCount":4,"averageRating":3.38}
{"releaseYear":1993,"title":"Schindler's List","watches":233,"completedWatches":222,"completionRatePct":95.28,"reviewCount":18,"averageRating":3.92}
{"releaseYear":2016,"title":"Hunt for the Wilderpeople","watches":84,"completedWatches":80,"completionRatePct":95.24,"reviewCount":10,"averageRating":3.9}
{"releaseYear":2010,"title":"Inception","watches":230,"completedWatches":219,"completionRatePct":95.22,"reviewCount":12,"averageRating":3.79}
{"releaseYear":1998,"title":"American History X","watches":242,"completedWatches":230,"completionRatePct":95.04,"reviewCount":25,"averageRating":4.02}
{"releaseYear":2014,"title":"Nightcrawler","watches":181,"completedWatches":172,"completionRatePct":95.03,"reviewCount":16,"averageRating":4}
{"releaseYear":1982,"title":"Monty Python: Live at The Hollywood Bowl","watches":40,"completedWatches":38,"completionRatePct":95,"reviewCount":3,"averageRating":4.17}
{"releaseYear":2018,"title":"Spider-Man: Into the Spider-Verse","watches":117,"completedWatches":111,"completionRatePct":94.87,"reviewCount":16,"averageRating":4.16}
{"releaseYear":2002,"title":"Catch Me If You Can","watches":244,"completedWatches":231,"completionRatePct":94.67,"reviewCount":25,"averageRating":3.92}
{"releaseYear":1994,"title":"Pulp Fiction","watches":281,"completedWatches":266,"completionRatePct":94.66,"reviewCount":29,"averageRating":4.34}
{"releaseYear":2013,"title":"Her","watches":184,"completedWatches":174,"completionRatePct":94.57,"reviewCount":22,"averageRating":4.07}
{"releaseYear":1997,"title":"Donnie Brasco","watches":147,"completedWatches":139,"completionRatePct":94.56,"reviewCount":13,"averageRating":3.65}
{"releaseYear":1975,"title":"Jaws","watches":243,"completedWatches":229,"completionRatePct":94.24,"reviewCount":28,"averageRating":3.84}
{"releaseYear":1996,"title":"Trainspotting","watches":243,"completedWatches":229,"completionRatePct":94.24,"reviewCount":22,"averageRating":3.86}
{"releaseYear":2012,"title":"Django Unchained","watches":238,"completedWatches":224,"completionRatePct":94.12,"reviewCount":22,"averageRating":4.2}
```

![Q7 captured command and output](../screenshots/q07-completion-vs-rating.png){ width=90% }

**Insight and scope.** Many completed flags use the same MovieLens ratings as the reviews. The association is built into the seed and cannot show causation. The saved output and screenshot above contain the observed records.

## Q8: Which users binge-watched (3 or more episodes of one series on one day)?

**Explanation.** Group completed series sessions by user, series, and the user's local calendar day. Count distinct episodes, then show up to 25 qualifying groups.

**Query source:** `queries/complex/q08-binge-watchers.js`

```javascript
// Q8: Which users binge-watched 3 or more distinct episodes of one series on one local day?
// Intent: Deduplicate completed episodes before counting, using each user's IANA time zone.
// Collections: watch_events, users, titles.
const result = db.watch_events.aggregate([
  { $match: { completed: true, season: { $exists: true }, episode: { $exists: true } } },
  { $lookup: { from: 'users', localField: 'userId', foreignField: '_id', as: 'user' } },
  { $unwind: '$user' },
  { $lookup: { from: 'titles', localField: 'titleId', foreignField: '_id', as: 'title' } },
  { $unwind: '$title' },
  { $match: { 'title.type': 'series' } },
  { $set: {
    localDay: { $dateTrunc: {
      date: '$startedAt', unit: 'day', timezone: '$user.timezone'
    } }
  } },
  { $group: {
    _id: {
      userId: '$userId', titleId: '$titleId', localDay: '$localDay',
      season: '$season', episode: '$episode'
    },
    name: { $first: '$user.name' },
    timezone: { $first: '$user.timezone' },
    title: { $first: '$title.name' }
  } },
  { $group: {
    _id: { userId: '$_id.userId', titleId: '$_id.titleId', localDay: '$_id.localDay' },
    user: { $first: '$name' }, timezone: { $first: '$timezone' },
    series: { $first: '$title' },
    distinctEpisodes: { $sum: 1 },
    episodes: { $push: { season: '$_id.season', episode: '$_id.episode' } }
  } },
  { $match: { distinctEpisodes: { $gte: 3 } } },
  { $project: {
    _id: 0, userId: '$_id.userId', titleId: '$_id.titleId',
    user: 1, series: 1, localDay: '$_id.localDay', timezone: 1,
    distinctEpisodes: 1, episodes: 1
  } },
  { $sort: { distinctEpisodes: -1, localDay: -1, user: 1 } },
  { $facet: {
    matches: [{ $count: 'count' }],
    rows: [{ $limit: 25 }]
  } }
]).toArray()[0];
printjson({ totalBinges: result.matches[0]?.count || 0, showingTop: result.rows.length });
result.rows.forEach(row => printjson(EJSON.stringify(row)));
```

**Saved terminal output:** `docs/query-output/q08-binge-watchers.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/complex/q08-binge-watchers.js
{
  totalBinges: 1,
  showingTop: 1
}
{"user":"Meera Singh","timezone":"Asia/Kolkata","series":"Blood & Water","distinctEpisodes":3,"episodes":[{"season":1,"episode":3},{"season":1,"episode":2},{"season":1,"episode":1}],"userId":{"$oid":"01000000000000000000001c"},"titleId":{"$oid":"020000000000000000000002"},"localDay":{"$date":"2023-06-11T18:30:00Z"}}
```

![Q8 captured command and output](../screenshots/q08-binge-watchers.png){ width=90% }

**Insight and scope.** Replays do not count as new episodes. This query shows at most 25 synthetic binge groups, not every qualifying group. The saved output and screenshot above contain the observed records.

## Q9: What is the monthly revenue and churn per plan?

**Explanation.** Group generated payments by UTC payment month and plan. Divide current-plan cancellations that month by users active at its start.

**Query source:** `queries/complex/q09-revenue-and-churn.js`

```javascript
// Q9: What is the monthly revenue and churn per plan?
// Intent: Sum actual payments by UTC payment month; churn is cancellations in that month
// divided by subscribers active at its start (null when that denominator is zero).
// Collections: payments, plans, users. Months shown have at least one payment.
const monthly = db.payments.aggregate([
  { $group: {
    _id: { plan: '$plan', month: { $dateTrunc: { date: '$paidAt', unit: 'month', timezone: 'UTC' } } },
    revenueInr: { $sum: '$amountInr' }, payments: { $sum: 1 }
  } },
  { $lookup: { from: 'plans', localField: '_id.plan', foreignField: 'name', as: 'planDetails' } },
  { $unwind: '$planDetails' },
  { $set: { nextMonth: { $dateAdd: { startDate: '$_id.month', unit: 'month', amount: 1 } } } },
  { $lookup: {
    from: 'users',
    let: { plan: '$_id.plan', month: '$_id.month', nextMonth: '$nextMonth' },
    pipeline: [
      { $match: { $expr: { $eq: ['$subscription.plan', '$$plan'] } } },
      { $facet: {
        activeAtMonthStart: [
          { $match: { $expr: { $and: [
            { $lte: ['$subscription.startedAt', '$$month'] },
            { $or: [
              { $eq: ['$subscription.endedAt', null] },
              { $gt: ['$subscription.endedAt', '$$month'] }
            ] }
          ] } } },
          { $count: 'count' }
        ],
        cancelledDuringMonth: [
          { $match: { $expr: { $and: [
            { $eq: ['$subscription.status', 'cancelled'] },
            { $gte: ['$subscription.endedAt', '$$month'] },
            { $lt: ['$subscription.endedAt', '$$nextMonth'] }
          ] } } },
          { $count: 'count' }
        ]
      } }
    ], as: 'subscriberStats'
  } },
  { $set: {
    activeAtMonthStart: { $ifNull: [{ $first: { $first: '$subscriberStats.activeAtMonthStart' } }, null] },
    cancelledDuringMonth: { $ifNull: [{ $first: { $first: '$subscriberStats.cancelledDuringMonth' } }, null] }
  } },
  { $set: {
    activeAtMonthStart: { $ifNull: ['$activeAtMonthStart.count', 0] },
    cancelledDuringMonth: { $ifNull: ['$cancelledDuringMonth.count', 0] }
  } },
  { $project: {
    _id: 0, month: '$_id.month', plan: '$_id.plan', planPriceInr: '$planDetails.priceInr',
    payments: 1, revenueInr: 1, activeAtMonthStart: 1, cancelledDuringMonth: 1,
    churnRatePct: { $cond: [
      { $gt: ['$activeAtMonthStart', 0] },
      { $round: [{ $multiply: [{ $divide: ['$cancelledDuringMonth', '$activeAtMonthStart'] }, 100] }, 2] },
      null
    ] }
  } },
  { $sort: { month: 1, plan: 1 } }
]).toArray();
printjson({ totalPlanMonths: monthly.length, showingFirst: Math.min(20, monthly.length) });
monthly.slice(0, 20).forEach(row => printjson(EJSON.stringify(row)));
```

**Saved terminal output:** `docs/query-output/q09-revenue-and-churn.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/complex/q09-revenue-and-churn.js
{
  totalPlanMonths: 63,
  showingFirst: 20
}
{"revenueInr":14925,"payments":75,"activeAtMonthStart":75,"cancelledDuringMonth":0,"month":{"$date":"2025-01-01T00:00:00Z"},"plan":"basic","planPriceInr":199,"churnRatePct":0}
{"revenueInr":47377,"payments":73,"activeAtMonthStart":73,"cancelledDuringMonth":0,"month":{"$date":"2025-01-01T00:00:00Z"},"plan":"premium","planPriceInr":649,"churnRatePct":0}
{"revenueInr":40419,"payments":81,"activeAtMonthStart":81,"cancelledDuringMonth":0,"month":{"$date":"2025-01-01T00:00:00Z"},"plan":"standard","planPriceInr":499,"churnRatePct":0}
{"revenueInr":33233,"payments":167,"activeAtMonthStart":167,"cancelledDuringMonth":0,"month":{"$date":"2025-02-01T00:00:00Z"},"plan":"basic","planPriceInr":199,"churnRatePct":0}
{"revenueInr":94105,"payments":145,"activeAtMonthStart":145,"cancelledDuringMonth":0,"month":{"$date":"2025-02-01T00:00:00Z"},"plan":"premium","planPriceInr":649,"churnRatePct":0}
{"revenueInr":74850,"payments":150,"activeAtMonthStart":150,"cancelledDuringMonth":0,"month":{"$date":"2025-02-01T00:00:00Z"},"plan":"standard","planPriceInr":499,"churnRatePct":0}
{"revenueInr":51939,"payments":261,"activeAtMonthStart":261,"cancelledDuringMonth":0,"month":{"$date":"2025-03-01T00:00:00Z"},"plan":"basic","planPriceInr":199,"churnRatePct":0}
{"revenueInr":154462,"payments":238,"activeAtMonthStart":238,"cancelledDuringMonth":0,"month":{"$date":"2025-03-01T00:00:00Z"},"plan":"premium","planPriceInr":649,"churnRatePct":0}
{"revenueInr":116267,"payments":233,"activeAtMonthStart":233,"cancelledDuringMonth":0,"month":{"$date":"2025-03-01T00:00:00Z"},"plan":"standard","planPriceInr":499,"churnRatePct":0}
{"revenueInr":67262,"payments":338,"activeAtMonthStart":338,"cancelledDuringMonth":0,"month":{"$date":"2025-04-01T00:00:00Z"},"plan":"basic","planPriceInr":199,"churnRatePct":0}
{"revenueInr":207031,"payments":319,"activeAtMonthStart":319,"cancelledDuringMonth":0,"month":{"$date":"2025-04-01T00:00:00Z"},"plan":"premium","planPriceInr":649,"churnRatePct":0}
{"revenueInr":157185,"payments":315,"activeAtMonthStart":315,"cancelledDuringMonth":0,"month":{"$date":"2025-04-01T00:00:00Z"},"plan":"standard","planPriceInr":499,"churnRatePct":0}
{"revenueInr":86565,"payments":435,"activeAtMonthStart":435,"cancelledDuringMonth":0,"month":{"$date":"2025-05-01T00:00:00Z"},"plan":"basic","planPriceInr":199,"churnRatePct":0}
{"revenueInr":263494,"payments":406,"activeAtMonthStart":406,"cancelledDuringMonth":0,"month":{"$date":"2025-05-01T00:00:00Z"},"plan":"premium","planPriceInr":649,"churnRatePct":0}
{"revenueInr":193113,"payments":387,"activeAtMonthStart":387,"cancelledDuringMonth":0,"month":{"$date":"2025-05-01T00:00:00Z"},"plan":"standard","planPriceInr":499,"churnRatePct":0}
{"revenueInr":102684,"payments":516,"activeAtMonthStart":516,"cancelledDuringMonth":0,"month":{"$date":"2025-06-01T00:00:00Z"},"plan":"basic","planPriceInr":199,"churnRatePct":0}
{"revenueInr":325798,"payments":502,"activeAtMonthStart":502,"cancelledDuringMonth":0,"month":{"$date":"2025-06-01T00:00:00Z"},"plan":"premium","planPriceInr":649,"churnRatePct":0}
{"revenueInr":225548,"payments":452,"activeAtMonthStart":452,"cancelledDuringMonth":0,"month":{"$date":"2025-06-01T00:00:00Z"},"plan":"standard","planPriceInr":499,"churnRatePct":0}
{"revenueInr":118405,"payments":595,"activeAtMonthStart":595,"cancelledDuringMonth":0,"month":{"$date":"2025-07-01T00:00:00Z"},"plan":"basic","planPriceInr":199,"churnRatePct":0}
{"revenueInr":384208,"payments":592,"activeAtMonthStart":592,"cancelledDuringMonth":0,"month":{"$date":"2025-07-01T00:00:00Z"},"plan":"premium","planPriceInr":649,"churnRatePct":0}
```

![Q9 captured command and output](../screenshots/q09-revenue-and-churn.png){ width=90% }

**Insight and scope.** The output covers months with payments. It describes generated billing, not audited revenue. A current subscription snapshot cannot track all past plan changes. The saved output and screenshot above contain the observed records.

## Q10: How does device usage change by hour of day?

**Explanation.** Group events and watch minutes by user-local hour and device. Show six-hour dayparts and each device's cumulative hourly event share.

**Query source:** `queries/complex/q10-device-usage-by-hour.js`

```javascript
// Q10: How does device usage change by hour of day?
// Intent: Compare local-hour device use, daypart totals, and each device's cumulative
// share of its own daily-profile events as hours advance (not chronological dates).
// Collections: watch_events, users (IANA timezone per user).
const usage = db.watch_events.aggregate([
  { $lookup: { from: 'users', localField: 'userId', foreignField: '_id', as: 'user' } },
  { $unwind: '$user' },
  { $set: { localHour: { $hour: { date: '$startedAt', timezone: '$user.timezone' } } } },
  { $facet: {
    hourlyByDevice: [
      { $group: {
        _id: { device: '$device', hour: '$localHour' },
        events: { $sum: 1 }, minutesWatched: { $sum: '$minutesWatched' }
      } },
      { $setWindowFields: {
        partitionBy: '$_id.device', sortBy: { '_id.hour': 1 },
        output: {
          runningEvents: { $sum: '$events', window: { documents: ['unbounded', 'current'] } },
          deviceEvents: { $sum: '$events', window: { documents: ['unbounded', 'unbounded'] } }
        }
      } },
      { $project: {
        _id: 0, device: '$_id.device', hour: '$_id.hour', events: 1,
        minutesWatched: 1, runningEvents: 1,
        runningSharePct: { $round: [{ $multiply: [{ $divide: ['$runningEvents', '$deviceEvents'] }, 100] }, 2] }
      } },
      { $sort: { hour: 1, device: 1 } }
    ],
    dayparts: [
      { $bucket: {
        groupBy: '$localHour', boundaries: [0, 6, 12, 18, 24],
        output: { events: { $sum: 1 }, minutesWatched: { $sum: '$minutesWatched' } }
      } },
      { $project: {
        _id: 0, startHour: '$_id',
        daypart: { $switch: { branches: [
          { case: { $eq: ['$_id', 0] }, then: 'night (00–06)' },
          { case: { $eq: ['$_id', 6] }, then: 'morning (06–12)' },
          { case: { $eq: ['$_id', 12] }, then: 'afternoon (12–18)' }
        ], default: 'evening (18–24)' } },
        events: 1, minutesWatched: 1
      } }
    ]
  } }
]).toArray()[0];
printjson({ hourlyDeviceRows: usage.hourlyByDevice.length, dayparts: usage.dayparts.length });
const byHour = new Map();
for (const row of usage.hourlyByDevice) {
  if (!byHour.has(row.hour)) byHour.set(row.hour, []);
  byHour.get(row.hour).push(row);
}
for (const [hour, devices] of byHour) printjson(EJSON.stringify({ hour, devices }));
usage.dayparts.forEach(row => printjson(EJSON.stringify(row)));
```

**Saved terminal output:** `docs/query-output/q10-device-usage-by-hour.txt`

```text
Command: docker compose exec -T mongo mongosh --quiet bingeling queries/complex/q10-device-usage-by-hour.js
{
  hourlyDeviceRows: 96,
  dayparts: 4
}
{"hour":0,"devices":[{"events":631,"minutesWatched":64100,"runningEvents":631,"device":"mobile","hour":0,"runningSharePct":5},{"events":575,"minutesWatched":58939,"runningEvents":575,"device":"tablet","hour":0,"runningSharePct":4.62},{"events":641,"minutesWatched":66514,"runningEvents":641,"device":"tv","hour":0,"runningSharePct":5.14},{"events":613,"minutesWatched":64875,"runningEvents":613,"device":"web","hour":0,"runningSharePct":4.92}]}
{"hour":1,"devices":[{"events":561,"minutesWatched":55995,"runningEvents":1192,"device":"mobile","hour":1,"runningSharePct":9.45},{"events":516,"minutesWatched":51411,"runningEvents":1091,"device":"tablet","hour":1,"runningSharePct":8.76},{"events":532,"minutesWatched":55012,"runningEvents":1173,"device":"tv","hour":1,"runningSharePct":9.4},{"events":575,"minutesWatched":58834,"runningEvents":1188,"device":"web","hour":1,"runningSharePct":9.54}]}
{"hour":2,"devices":[{"events":537,"minutesWatched":54088,"runningEvents":1729,"device":"mobile","hour":2,"runningSharePct":13.7},{"events":508,"minutesWatched":51663,"runningEvents":1599,"device":"tablet","hour":2,"runningSharePct":12.84},{"events":541,"minutesWatched":57366,"runningEvents":1714,"device":"tv","hour":2,"runningSharePct":13.74},{"events":569,"minutesWatched":58642,"runningEvents":1757,"device":"web","hour":2,"runningSharePct":14.11}]}
{"hour":3,"devices":[{"events":455,"minutesWatched":46839,"runningEvents":2184,"device":"mobile","hour":3,"runningSharePct":17.31},{"events":451,"minutesWatched":46035,"runningEvents":2050,"device":"tablet","hour":3,"runningSharePct":16.46},{"events":475,"minutesWatched":49721,"runningEvents":2189,"device":"tv","hour":3,"runningSharePct":17.54},{"events":485,"minutesWatched":49474,"runningEvents":2242,"device":"web","hour":3,"runningSharePct":18.01}]}
{"hour":4,"devices":[{"events":491,"minutesWatched":50844,"runningEvents":2675,"device":"mobile","hour":4,"runningSharePct":21.2},{"events":501,"minutesWatched":51264,"runningEvents":2551,"device":"tablet","hour":4,"runningSharePct":20.49},{"events":483,"minutesWatched":49272,"runningEvents":2672,"device":"tv","hour":4,"runningSharePct":21.42},{"events":480,"minutesWatched":48367,"runningEvents":2722,"device":"web","hour":4,"runningSharePct":21.86}]}
{"hour":5,"devices":[{"events":393,"minutesWatched":40168,"runningEvents":3068,"device":"mobile","hour":5,"runningSharePct":24.31},{"events":409,"minutesWatched":42715,"runningEvents":2960,"device":"tablet","hour":5,"runningSharePct":23.77},{"events":409,"minutesWatched":42712,"runningEvents":3081,"device":"tv","hour":5,"runningSharePct":24.69},{"events":406,"minutesWatched":42213,"runningEvents":3128,"device":"web","hour":5,"runningSharePct":25.12}]}
{"hour":6,"devices":[{"events":326,"minutesWatched":33430,"runningEvents":3394,"device":"mobile","hour":6,"runningSharePct":26.9},{"events":350,"minutesWatched":36459,"runningEvents":3310,"device":"tablet","hour":6,"runningSharePct":26.58},{"events":369,"minutesWatched":37478,"runningEvents":3450,"device":"tv","hour":6,"runningSharePct":27.65},{"events":368,"minutesWatched":38339,"runningEvents":3496,"device":"web","hour":6,"runningSharePct":28.08}]}
{"hour":7,"devices":[{"events":430,"minutesWatched":44874,"runningEvents":3824,"device":"mobile","hour":7,"runningSharePct":30.31},{"events":438,"minutesWatched":46055,"runningEvents":3748,"device":"tablet","hour":7,"runningSharePct":30.1},{"events":412,"minutesWatched":43983,"runningEvents":3862,"device":"tv","hour":7,"runningSharePct":30.95},{"events":416,"minutesWatched":43256,"runningEvents":3912,"device":"web","hour":7,"runningSharePct":31.42}]}
{"hour":8,"devices":[{"events":414,"minutesWatched":42510,"runningEvents":4238,"device":"mobile","hour":8,"runningSharePct":33.59},{"events":400,"minutesWatched":41562,"runningEvents":4148,"device":"tablet","hour":8,"runningSharePct":33.31},{"events":426,"minutesWatched":44611,"runningEvents":4288,"device":"tv","hour":8,"runningSharePct":34.37},{"events":406,"minutesWatched":43226,"runningEvents":4318,"device":"web","hour":8,"runningSharePct":34.68}]}
{"hour":9,"devices":[{"events":507,"minutesWatched":51616,"runningEvents":4745,"device":"mobile","hour":9,"runningSharePct":37.61},{"events":481,"minutesWatched":49848,"runningEvents":4629,"device":"tablet","hour":9,"runningSharePct":37.17},{"events":467,"minutesWatched":46873,"runningEvents":4755,"device":"tv","hour":9,"runningSharePct":38.11},{"events":465,"minutesWatched":48041,"runningEvents":4783,"device":"web","hour":9,"runningSharePct":38.41}]}
{"hour":10,"devices":[{"events":505,"minutesWatched":51362,"runningEvents":5250,"device":"mobile","hour":10,"runningSharePct":41.61},{"events":469,"minutesWatched":46521,"runningEvents":5098,"device":"tablet","hour":10,"runningSharePct":40.94},{"events":492,"minutesWatched":49269,"runningEvents":5247,"device":"tv","hour":10,"runningSharePct":42.05},{"events":485,"minutesWatched":47637,"runningEvents":5268,"device":"web","hour":10,"runningSharePct":42.31}]}
{"hour":11,"devices":[{"events":392,"minutesWatched":40250,"runningEvents":5642,"device":"mobile","hour":11,"runningSharePct":44.71},{"events":410,"minutesWatched":42843,"runningEvents":5508,"device":"tablet","hour":11,"runningSharePct":44.23},{"events":431,"minutesWatched":42292,"runningEvents":5678,"device":"tv","hour":11,"runningSharePct":45.51},{"events":360,"minutesWatched":37278,"runningEvents":5628,"device":"web","hour":11,"runningSharePct":45.2}]}
{"hour":12,"devices":[{"events":434,"minutesWatched":45215,"runningEvents":6076,"device":"mobile","hour":12,"runningSharePct":48.15},{"events":417,"minutesWatched":44470,"runningEvents":5925,"device":"tablet","hour":12,"runningSharePct":47.58},{"events":413,"minutesWatched":42230,"runningEvents":6091,"device":"tv","hour":12,"runningSharePct":48.82},{"events":415,"minutesWatched":42421,"runningEvents":6043,"device":"web","hour":12,"runningSharePct":48.53}]}
{"hour":13,"devices":[{"events":537,"minutesWatched":56431,"runningEvents":6613,"device":"mobile","hour":13,"runningSharePct":52.41},{"events":524,"minutesWatched":53237,"runningEvents":6449,"device":"tablet","hour":13,"runningSharePct":51.79},{"events":513,"minutesWatched":50639,"runningEvents":6604,"device":"tv","hour":13,"runningSharePct":52.93},{"events":499,"minutesWatched":49077,"runningEvents":6542,"device":"web","hour":13,"runningSharePct":52.54}]}
{"hour":14,"devices":[{"events":561,"minutesWatched":57464,"runningEvents":7174,"device":"mobile","hour":14,"runningSharePct":56.86},{"events":559,"minutesWatched":56953,"runningEvents":7008,"device":"tablet","hour":14,"runningSharePct":56.28},{"events":575,"minutesWatched":57326,"runningEvents":7179,"device":"tv","hour":14,"runningSharePct":57.54},{"events":559,"minutesWatched":56675,"runningEvents":7101,"device":"web","hour":14,"runningSharePct":57.03}]}
{"hour":15,"devices":[{"events":537,"minutesWatched":56295,"runningEvents":7711,"device":"mobile","hour":15,"runningSharePct":61.11},{"events":552,"minutesWatched":57382,"runningEvents":7560,"device":"tablet","hour":15,"runningSharePct":60.71},{"events":512,"minutesWatched":52772,"runningEvents":7691,"device":"tv","hour":15,"runningSharePct":61.64},{"events":546,"minutesWatched":55703,"runningEvents":7647,"device":"web","hour":15,"runningSharePct":61.41}]}
{"hour":16,"devices":[{"events":571,"minutesWatched":58578,"runningEvents":8282,"device":"mobile","hour":16,"runningSharePct":65.64},{"events":561,"minutesWatched":58103,"runningEvents":8121,"device":"tablet","hour":16,"runningSharePct":65.21},{"events":566,"minutesWatched":57895,"runningEvents":8257,"device":"tv","hour":16,"runningSharePct":66.18},{"events":593,"minutesWatched":62985,"runningEvents":8240,"device":"web","hour":16,"runningSharePct":66.17}]}
{"hour":17,"devices":[{"events":651,"minutesWatched":66460,"runningEvents":8933,"device":"mobile","hour":17,"runningSharePct":70.8},{"events":653,"minutesWatched":68187,"runningEvents":8774,"device":"tablet","hour":17,"runningSharePct":70.46},{"events":602,"minutesWatched":61035,"runningEvents":8859,"device":"tv","hour":17,"runningSharePct":71},{"events":619,"minutesWatched":64993,"runningEvents":8859,"device":"web","hour":17,"runningSharePct":71.15}]}
{"hour":18,"devices":[{"events":574,"minutesWatched":58479,"runningEvents":9507,"device":"mobile","hour":18,"runningSharePct":75.34},{"events":657,"minutesWatched":68002,"runningEvents":9431,"device":"tablet","hour":18,"runningSharePct":75.73},{"events":588,"minutesWatched":60938,"runningEvents":9447,"device":"tv","hour":18,"runningSharePct":75.72},{"events":594,"minutesWatched":61863,"runningEvents":9453,"device":"web","hour":18,"runningSharePct":75.92}]}
{"hour":19,"devices":[{"events":637,"minutesWatched":65576,"runningEvents":10144,"device":"mobile","hour":19,"runningSharePct":80.39},{"events":675,"minutesWatched":69752,"runningEvents":10106,"device":"tablet","hour":19,"runningSharePct":81.15},{"events":661,"minutesWatched":68260,"runningEvents":10108,"device":"tv","hour":19,"runningSharePct":81.01},{"events":662,"minutesWatched":68818,"runningEvents":10115,"device":"web","hour":19,"runningSharePct":81.23}]}
{"hour":20,"devices":[{"events":570,"minutesWatched":57883,"runningEvents":10714,"device":"mobile","hour":20,"runningSharePct":84.91},{"events":593,"minutesWatched":60398,"runningEvents":10699,"device":"tablet","hour":20,"runningSharePct":85.92},{"events":634,"minutesWatched":65913,"runningEvents":10742,"device":"tv","hour":20,"runningSharePct":86.09},{"events":549,"minutesWatched":55737,"runningEvents":10664,"device":"web","hour":20,"runningSharePct":85.64}]}
{"hour":21,"devices":[{"events":665,"minutesWatched":67517,"runningEvents":11379,"device":"mobile","hour":21,"runningSharePct":90.18},{"events":573,"minutesWatched":58802,"runningEvents":11272,"device":"tablet","hour":21,"runningSharePct":90.52},{"events":601,"minutesWatched":59735,"runningEvents":11343,"device":"tv","hour":21,"runningSharePct":90.91},{"events":602,"minutesWatched":61711,"runningEvents":11266,"device":"web","hour":21,"runningSharePct":90.48}]}
{"hour":22,"devices":[{"events":626,"minutesWatched":64740,"runningEvents":12005,"device":"mobile","hour":22,"runningSharePct":95.14},{"events":616,"minutesWatched":64113,"runningEvents":11888,"device":"tablet","hour":22,"runningSharePct":95.46},{"events":583,"minutesWatched":59502,"runningEvents":11926,"device":"tv","hour":22,"runningSharePct":95.58},{"events":623,"minutesWatched":64678,"runningEvents":11889,"device":"web","hour":22,"runningSharePct":95.48}]}
{"hour":23,"devices":[{"events":613,"minutesWatched":62773,"runningEvents":12618,"device":"mobile","hour":23,"runningSharePct":100},{"events":565,"minutesWatched":58246,"runningEvents":12453,"device":"tablet","hour":23,"runningSharePct":100},{"events":551,"minutesWatched":56320,"runningEvents":12477,"device":"tv","hour":23,"runningSharePct":100},{"events":563,"minutesWatched":58712,"runningEvents":12452,"device":"web","hour":23,"runningSharePct":100}]}
{"events":12237,"minutesWatched":1257063,"startHour":0,"daypart":"night (00–06)"}
{"events":10219,"minutesWatched":1049613,"startHour":6,"daypart":"morning (06–12)"}
{"events":12969,"minutesWatched":1332526,"startHour":12,"daypart":"afternoon (12–18)"}
{"events":14575,"minutesWatched":1498468,"startHour":18,"daypart":"evening (18–24)"}
```

![Q10 captured command and output](../screenshots/q10-device-usage-by-hour.png){ width=90% }

**Insight and scope.** Devices are assigned by the generator, and many hours come from rating timestamps. This result cannot establish real hourly demand. The saved output and screenshot above contain the observed records.

# Insights

The catalogue queries show available titles, languages, and cast matches. Country-genre minutes, completion, binge groups, and hourly device use are properties of this constructed dataset. They are not market demand estimates. Multi-genre titles appear in several genre totals. Completion and rating are linked by the generator's rating threshold, so their association is partly built into the data. Likewise, the generator assigns countries, devices, and plan states. Monthly payments are simulated. The saved outputs above give the exact result values for each query, subject to its stated scope.

# Conclusion and limitations

This case study demonstrates document modeling, indexed lookup designs, aggregation, and a repeatable source-to-report trail. Every query block comes from its executable source. Each result excerpt comes from a saved terminal run. Each numbered screenshot is required at build time. These checks prevent a report with missing evidence, but they cannot prove a screenshot came from a specific database state.

Netflix catalogue labels are a dated sample. MovieLens ratings are not viewing logs [R12, R13]. User identities, country and time zone, devices, episodes, subscriptions, and payments are constructed. The generator derives many completion flags from ratings; this prevents independent inference from the Q7 comparison. A rating timestamp is not a watch-start time; Q4, Q8, and Q10 illustrate query mechanics rather than real viewing rhythms. A current subscription record cannot reconstruct all past plan changes. Payments do not prove collected or recognized revenue. Do not use these results for forecasts. Source terms restrict reuse of the MovieLens-derived records [R1, R12, R15].

# References

- [R1] Project domain analysis. docs/domain-analysis.md
- [R2] Project data model. docs/data-model.md
- [R3] Project fixed questions. docs/questions.md
- [R4] Project guidelines. GUIDELINES.md
- [R5] Netflix, What We Watched: The Second Half of 2025. https://about.netflix.com/news/what-we-watched-the-second-half-of-2025
- [R6] FICCI-EY, Indian media and entertainment sector in 2025. https://www.ey.com/en_in/newsroom/2026/03/india-s-media-and-entertainment-sector-grew-9-percent-to-inr-2-point-78-trillion-in-2025-driven-by-digital-and-live-experiences-ficci-ey-report
- [R7] Government of India, 2024 video subscription revenue. https://www.pib.gov.in/PressReleasePage.aspx?PRID=2205233&lang=2&reg=3
- [R8] MongoDB, Data Modeling Best Practices. https://www.mongodb.com/docs/manual/data-modeling/best-practices/
- [R9] MongoDB, Unbounded Arrays Anti-Pattern. https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/unbounded-arrays/
- [R10] MongoDB, SonyLIV content management case study. https://www.mongodb.com/company/blog/innovation/sonyliv-improves-cms-performance-by-98-percent-on-atlas
- [R11] IMDb, Non-Commercial Datasets. https://data.imdb.com/non-commercial-datasets/
- [R12] MovieLens 32M, README and licence. https://files.grouplens.org/datasets/movielens/ml-32m-README.html
- [R13] Kaggle, Netflix titles dataset metadata. https://www.kaggle.com/api/v1/datasets/view/shivamb/netflix-shows
- [R14] ZEE5 FY25 viewing report, Deccan Chronicle. https://www.deccanchronicle.com/entertainment/ott/zee5-clocks-105-billion-watch-minutes-in-fy25-amid-renewed-regional-push-1898817
- [R15] Harper, F. Maxwell, and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems 5(4), Article 19. https://doi.org/10.1145/2827872

**Evidence files:** `data/manifest.json`, the six `data/*.json` arrays, ten `queries/**/*.js` files, ten `docs/query-output/*.txt` files, and ten matching `screenshots/*.png`. These files fix the reproducible scope of this report.
