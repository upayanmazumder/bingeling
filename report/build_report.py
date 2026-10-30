#!/usr/bin/env python3
# ruff: noqa: E501
"""Write a student-facing case study from the recorded seed and query evidence."""

import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "report/Bingeling-report.md"
DATA = ROOT / "data"
OUTPUT = ROOT / "docs/query-output"
SCREENSHOTS = ROOT / "screenshots"

QUESTIONS = (
    (
        "simple",
        "q01-thrillers-after-2018",
        "List all Thriller movies released after 2018, newest first.",
    ),
    ("simple", "q02-active-premium-count", "How many users have an active premium subscription?"),
    ("simple", "q03-catalogue-languages", "Which languages are in the catalogue?"),
    ("simple", "q04-recent-watches", "Show the 10 most recent watch events of one user."),
    ("simple", "q05-titles-by-actor", "Find titles that feature a given actor."),
    (
        "complex",
        "q06-top-genres-by-country",
        "What are the top 5 genres by total watch minutes in each country?",
    ),
    (
        "complex",
        "q07-completion-vs-rating",
        "What is the completion rate of each movie, with average rating?",
    ),
    (
        "complex",
        "q08-binge-watchers",
        "Which users binge-watched (3 or more episodes of one series on one day)?",
    ),
    ("complex", "q09-revenue-and-churn", "What is the monthly revenue and churn per plan?"),
    ("complex", "q10-device-usage-by-hour", "How does device usage change by hour of day?"),
)


def required(path):
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f"Missing or empty required evidence: {path.relative_to(ROOT)}")
    return path


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def code(text, language="text"):
    fence = "`" * max(3, max((len(group) for group in re.findall(r"`+", text)), default=0) + 1)
    if not text.endswith("\n"):
        text += "\n"
    return f"{fence}{language}\n{text}{fence}\n"


def image_is_png(path):
    raw = required(path).read_bytes()
    if (
        len(raw) < 1024
        or raw[:8] != b"\x89PNG\r\n\x1a\n"
        or raw[12:16] != b"IHDR"
        or b"IEND" not in raw[-32:]
    ):
        raise ValueError(f"Screenshot is not a complete PNG: {path.relative_to(ROOT)}")
    width, height = struct.unpack(">II", raw[16:24])
    if width < 500 or height < 100:
        raise ValueError(f"Screenshot is too small: {path.relative_to(ROOT)}")


def load_inputs():
    manifest = json.loads(required(DATA / "manifest.json").read_text(encoding="utf-8"))
    for field in ("demoUserId", "demoActor"):
        if not manifest.get(field):
            raise ValueError(f"data/manifest.json lacks {field}")
    collections = {}
    for name in ("users", "titles", "watch_events", "reviews", "plans", "payments"):
        path = required(DATA / f"{name}.json")
        collection = json.loads(path.read_text(encoding="utf-8"))
        recorded = manifest.get("files", {}).get(name, {})
        if (
            not collection
            or recorded.get("count") != len(collection)
            or recorded.get("sha256") != sha256_file(path)
        ):
            raise ValueError(f"data/{name}.json differs from its manifest")
        collections[name] = collection
    queries = []
    for group, stem, question in QUESTIONS:
        query = required(ROOT / "queries" / group / f"{stem}.js").read_text(encoding="utf-8")
        output = required(OUTPUT / f"{stem}.txt").read_text(encoding="utf-8")
        image_is_png(SCREENSHOTS / f"{stem}.png")
        if f"queries/{group}/{stem}.js" not in output.splitlines()[0] or not any(
            output.splitlines()[1:]
        ):
            raise ValueError(f"Saved output lacks query results: {stem}")
        queries.append((group, stem, question, query, output))
    image_is_png(SCREENSHOTS / "population.png")
    return manifest, collections, queries


EXPLANATIONS = [
    "A catalogue search uses a movie filter, the Thriller genre, and a release year after 2018. The query counts every match and displays at most ten titles in descending year order.",
    "This count checks two fields of the current subscription embedded in each user. A premium plan alone does not imply an active subscription.",
    "The distinct operation lists the language codes stored in the title collection. These codes describe the generated catalogue field, not verified audio tracks.",
    "The manifest identifies one demo user. A filter on `userId`, descending sort on `startedAt`, and limit of ten display that user's latest stored events.",
    "The embedded `cast` array lets a title search match the selected actor. The query also counts all matches, then displays at most ten alphabetically.",
    "The pipeline joins each event to its user and title. It groups minutes by user country and title genre, then ranks five genres per country. A title with several genres contributes its minutes to each genre.",
    "Two separate lookups collect watch counts and review averages for each movie. Separate groups avoid multiplying rows when a title has several watches and reviews. Completion rate equals completed watch records divided by all watch records, multiplied by 100. The query displays the first 20 movies after sorting by that rate.",
    "The pipeline joins events with users and series titles. It converts timestamps to each user's local day and groups by user, series, season, and episode. It removes repeated plays before counting distinct episodes. The final result reports the match count and displays at most 25 groups.",
    "The pipeline adds generated payment amounts by plan and UTC payment month. It joins plan prices and counts users by their current plan. Churn rate equals cancellations in that month divided by users active at the month's start, multiplied by 100. A zero denominator returns null. Only months with payments appear, and the query displays the first 20 plan-month rows.",
    "The pipeline joins each event to its user's time zone and extracts the local hour. It groups events and minutes by device and hour. A window calculation tracks each device's cumulative share across hours 0–23. Four six-hour buckets show totals by daypart.",
]


def rows(output):
    return [json.loads(line) for line in output.splitlines()[1:] if line.startswith('{"')]


def answer(number, output):
    records = rows(output)
    if number == 1:
        count = int(re.search(r"totalMatches:\s*(\d+)", output).group(1))
        return f"The seed catalogue has **{count}** matching films. The newest displayed films are **{records[0]['name']}** and **{records[1]['name']}**, both from {records[0]['releaseYear']}."
    if number == 2:
        count = int(re.search(r"activePremiumUsers:\s*(\d+)", output).group(1))
        return f"The current seed snapshot contains **{count} active premium users**."
    if number == 3:
        codes = re.findall(r"'([a-z]{2})'", output)
        return f"The catalogue contains **{len(codes)} language codes**: {', '.join(f'`{code}`' for code in codes)}."
    if number == 4:
        return f"For the selected user, the three newest stored events are episodes 3, 2, and 1 of **{records[0]['titleName']}** on 12 June 2023. They are the explicit sample binge scenario."
    if number == 5:
        count = int(re.search(r"totalMatches:\s*(\d+)", output).group(1))
        return f"**Adam Sandler** appears in **{count}** matching titles. The first displayed title in alphabetical order is **{records[0]['name']}**."
    if number == 6:
        india = next(record for record in records if record["country"] == "IN")
        top = india["topGenres"][0]
        return f"**Drama** ranks first in each of the four assigned countries. For India, it totals **{top['totalMinutes']:,} generated watch minutes**. Action and Comedy rank next in India's output."
    if number == 7:
        first = records[0]
        return f"The output covers **400 movies** and displays the first 20. **{first['title']}** leads this displayed order with **{first['completedWatches']} completed records out of {first['watches']}**, or **{first['completionRatePct']}%**. Its {first['reviewCount']} review has an average rating of {first['averageRating']} out of 5."
    if number == 8:
        record = records[0]
        return f"The query finds **one qualifying group**. The generated user **{record['user']}** has three distinct completed episodes of **{record['series']}**. All three fall on 12 June 2023 in the Asia/Kolkata time zone."
    if number == 9:
        row = next(
            record
            for record in records
            if record["plan"] == "premium" and record["month"]["$date"].startswith("2025-01")
        )
        return f"The query finds **63 plan-month rows** and displays the first 20. In January 2025, the premium plan has **₹{row['revenueInr']:,} in generated payments** from {row['payments']} payments. It has {row['cancelledDuringMonth']} cancellations among {row['activeAtMonthStart']} users active at the month start, so its reported churn rate is {row['churnRatePct']}%."
    if number == 10:
        dayparts = [record for record in records if "daypart" in record]
        peak = max(dayparts, key=lambda record: record["events"])
        return f"The query produces **96 device-hour groups** and four dayparts. The **{peak['daypart']}** bucket has the most generated records: **{peak['events']:,} events** and **{peak['minutesWatched']:,} minutes**."
    raise ValueError(number)


def example(doc, fields):
    return json.dumps({key: doc[key] for key in fields}, ensure_ascii=False, indent=2)


def build(manifest, collections, queries):
    parts = [
        "```{=typst}\n",
        "#set text(size: 10.5pt)\n",
        "#set par(leading: 0.65em, spacing: 0.55em)\n",
        "#show raw: set text(size: 8pt)\n",
        "#show heading: set block(above: 1.1em, below: 0.6em)\n",
        "#align(center)[\n",
        "  #v(22%)\n",
        '  #text(size: 27pt, weight: "bold")[Bingeling:]\n',
        "  #v(0.5cm)\n",
        "  #text(size: 18pt)[A Video Streaming Database Using MongoDB]\n",
        "  #v(2cm)\n",
        "  #text(size: 15pt)[Upayan Mazumder]\\\n",
        "  #text(size: 13pt)[24BDS0367]\\\n",
        "  #text(size: 13pt)[BCSE302L – Database Systems]\\\n",
        "  #text(size: 11pt)[22 October 2026]\n",
        "]\n#pagebreak()\n",
        "```\n\n",
        "# Introduction and domain analysis\n\n",
        "Bingeling is a small database for a sample video-streaming platform. Its catalogue contains movies and series. A user has a profile and a current subscription. The database also stores sample viewing activity, ratings, plan details, and payments. This case study uses MongoDB 7 and answers five simple and five complex questions with queries against populated collections.\n\n",
        "A viewer could search titles by genre or actor and inspect recent activity. A catalogue team could compare genres by country. A subscription team could examine plan counts and monthly records. These tasks need different data shapes: title details belong together, while viewing events and payments grow as separate records. This project models the records and queries. It does not stream video.\n\n",
        "# Database choice and design\n\n",
        "MongoDB stores a title as one document with arrays for genres and cast. A series also embeds its seasons and episodes. These lists have a limited size and usually appear with the title. The `users` collection embeds profiles and one current `subscription`. An index can support searches across documents. Aggregation pipelines combine collections and calculate grouped results for Q6–Q10 [3].\n\n",
        "The database keeps `watch_events`, `reviews`, and `payments` separate. A user can acquire many events, so embedding every event in a user document would make that document grow without a fixed limit. Event documents refer to users and titles by BSON `ObjectId`. The `titleName` copied into an event makes a history row easier to display, but it needs an update if a title name changes. MongoDB does not enforce these references as relational foreign keys.\n\n",
        "| Collection | Purpose and key fields | Links |\n|---|---|---|\n",
        "| `users` | `_id`, `name`, `country`, `timezone`, `profiles`, current `subscription` | `_id` from events, reviews, payments |\n",
        "| `titles` | `_id`, `type`, `name`, `releaseYear`, `genres`, `cast`, movie `runtimeMin` or series `seasons` | `_id` from events and reviews |\n",
        "| `watch_events` | `userId`, `titleId`, `startedAt`, `minutesWatched`, `completed`, `device` | users and titles |\n",
        "| `reviews` | `userId`, `titleId`, `rating`, `createdAt` | users and titles |\n",
        "| `plans` | `name`, `priceInr`, `screens`, `maxQuality` | plan name in users and payments |\n",
        "| `payments` | `userId`, `plan`, `amountInr`, `paidAt`, billing period | users and plans |\n\n",
        "The loader imports Extended JSON arrays with `$oid` and `$date`, then installs validators and indexes. A compound index on `watch_events.userId` and `startedAt` suits Q4. The `titles.genres` and `releaseYear` index suits Q1. A unique `(titleId, userId)` review index limits one rating per user and title. Payment indexes cover plan and billing period. These indexes describe the implemented access paths. The report does not claim a measured speed gain.\n\n",
        "# Data population\n\n",
        "The seed script uses fixed seed `367`. It selects 400 movies from a September 2021 Netflix catalogue snapshot and matches them by title and year to MovieLens movie links. It also selects 100 series from the catalogue. The catalogue supplies names, cast, categories, and release years [1]. MovieLens 32M supplies anonymous user IDs, ratings, and rating timestamps [2]. The script stores 5,000 ratings as `reviews` with empty text.\n\n",
        "The script generates names and `example.com` addresses for those anonymous IDs. It also generates countries, subscriptions, plans, billing records, devices, and series episodes. It uses 49,997 selected MovieLens rating rows to construct sample `watch_events` and adds three series events for one binge example. A rating timestamp is **not** a playback timestamp. For these movie records, a rating of at least 3 sets `completed` to true and `minutesWatched` to the movie runtime. Lower ratings produce a half-runtime record. The script generates the extra fields and sample viewing activity. It does not observe playback.\n\n",
        "The script writes six Extended JSON arrays. `scripts/load.sh` imports them into `bingeling`, and `scripts/schema.js` adds validators and indexes. The checked-in arrays contain these counts:\n\n",
        "| Collection | Documents |\n|---|---:|\n",
    ]
    for name in ("users", "titles", "watch_events", "reviews", "plans", "payments"):
        parts.append(f"| `{name}` | {len(collections[name]):,} |\n")
    parts += [
        "\nThe following field excerpts come from the checked-in arrays. The first is a movie title. The second is a sample event. They omit other stored fields.\n\n",
        "**Title excerpt**\n\n",
        code(
            example(collections["titles"][0], ("_id", "type", "name", "genres", "runtimeMin")),
            "json",
        ),
        "\n**Event excerpt**\n\n",
        code(
            example(
                collections["watch_events"][0],
                ("userId", "titleId", "startedAt", "minutesWatched", "completed", "origin"),
            ),
            "json",
        ),
        "\nThe population screenshot records the MongoDB counts from the existing demonstration.\n\n",
        "![MongoDB collection counts](../screenshots/population.png){ width=100% }\n\n",
        "# Dataset limits\n\n",
        "MovieLens records ratings, not video plays. The generator assigns event duration, device, completion, user names, locations, subscriptions, and payments. It infers the `language` code from title country rather than verified audio data. The generator adds the binge example deliberately. Thus Q4 and Q6–Q10 illustrate database questions, not actual viewer behaviour or collected revenue. Q7 completion and rating are not independent: the generator uses rating to set many completion flags. The Netflix catalogue is a dated selection, not a current complete service catalogue.\n\n",
    ]
    for group, heading in (
        ("simple", "Five simple questions"),
        ("complex", "Five complex questions"),
    ):
        parts.append(f"# {heading}\n\n")
        for query_group, stem, question, query, output in queries:
            if query_group != group:
                continue
            number = int(stem[1:3])
            executable = "\n".join(query.splitlines()[3:]) + "\n"
            parts += [
                f"## Q{number}. {question}\n\n",
                EXPLANATIONS[number - 1],
                "\n\n",
                f"**Query** (`queries/{group}/{stem}.js`):\n\n",
                code(executable, "javascript"),
                "\n",
                f"![Q{number} execution in mongosh](../screenshots/{stem}.png){{ width=100% }}\n\n",
                "**Answer.** ",
                answer(number, output),
                "\n\n",
            ]
    parts += [
        "# Findings and limitations\n\n",
        "The seed catalogue returns ten Thriller films after 2018 and five stored language codes. The current subscription snapshot contains 619 active premium users. Drama leads the genre-minute ranking in each of the four assigned countries. The single detected binge group is the inserted three-episode example. The Q10 evening bucket contains 14,575 generated events. These are answers for this seed, not estimates for a streaming service.\n\n",
        "The constructed events cannot measure real viewing time, completion, geography, or device choice. The Q9 payment totals and churn describe generated subscriptions. Q9 uses the current plan and its start and end dates, so it cannot reconstruct a subscriber's past plan changes. Only the first 20 of 63 plan-month rows appear in that query's displayed output.\n\n",
        "# Conclusion\n\n",
        "The six MongoDB collections store a catalogue, users, sample activity, ratings, plans, and payments. Five simple queries filter, count, or list documents. Five pipelines join collections and calculate grouped measures. The recorded outputs and screenshots show the implementation for this case study. The generated fields limit what its numbers can say about real viewers.\n\n",
        "# References\n\n",
        "[1] S. Bansal, “Netflix Movies and TV Shows,” Kaggle, September 2021. [Online]. Available: https://www.kaggle.com/datasets/shivamb/netflix-shows (CC0 catalogue snapshot).\n\n",
        "[2] GroupLens Research, “MovieLens 32M Dataset,” University of Minnesota. [Online]. Available: https://grouplens.org/datasets/movielens/32m/ and https://files.grouplens.org/datasets/movielens/ml-32m-README.html. Research and redistribution must follow the GroupLens terms. Commercial use requires permission. GroupLens and the University of Minnesota do not endorse Bingeling. See also F. M. Harper and J. A. Konstan, “The MovieLens Datasets: History and Context,” *ACM Transactions on Interactive Intelligent Systems*, vol. 5, no. 4, 2015, doi:10.1145/2827872.\n\n",
        "[3] MongoDB, “Data Modeling Best Practices.” [Online]. Available: https://www.mongodb.com/docs/manual/data-modeling/best-practices/.\n",
    ]
    return "".join(parts)


def main():
    manifest, collections, queries = load_inputs()
    SOURCE.write_text(build(manifest, collections, queries), encoding="utf-8")
    print(f"Generated {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
