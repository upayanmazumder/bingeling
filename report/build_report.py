#!/usr/bin/env python3
"""Generate the Bingeling report from checked-in evidence, not hand-copied queries."""

import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report" / "Bingeling-report.md"
DATA = ROOT / "data"
OUTPUT = ROOT / "docs" / "query-output"
SCREENSHOTS = ROOT / "screenshots"

QUESTIONS = [
    (
        "simple",
        "q01-thrillers-after-2018",
        "List all Thriller movies released after 2018, newest first.",
        "Filter the movie catalogue by genre and release year. Sort newer releases first.",
        "The generator intentionally selects recent linked Thrillers. Their presence is not proof of demand or an unbiased catalogue sample.",
    ),
    (
        "simple",
        "q02-active-premium-count",
        "How many users have an active premium subscription?",
        "Count the users whose current plan is premium and whose current status is active.",
        "The generator assigns each user a plan and status. This count measures the current synthetic snapshot, not subscriber growth.",
    ),
    (
        "simple",
        "q03-catalogue-languages",
        "Which languages are in the catalogue?",
        "List distinct language codes stored on title documents.",
        "The generator infers language from catalogue country. These codes are proxies, not confirmed audio-track languages or viewing shares.",
    ),
    (
        "simple",
        "q04-recent-watches",
        "Show the 10 most recent watch events of one user.",
        "Use the fixed demo user from the manifest. Sort that user's events by start time and limit the result to ten.",
        "Many recorded start times are MovieLens rating times, not watched-at times. The result demonstrates sorting, not true recent viewing.",
    ),
    (
        "simple",
        "q05-titles-by-actor",
        "Find titles that feature a given actor.",
        "Use the fixed demo actor from the manifest. Match the name in each title's embedded cast.",
        "This result checks a cast-based browse operation, not the actor's popularity.",
    ),
    (
        "complex",
        "q06-top-genres-by-country",
        "What are the top 5 genres by total watch minutes in each country?",
        "Join watch events to titles and users. Group watch minutes by country and genre, then rank genres within each country.",
        "Countries are assigned to anonymous rating IDs. Multi-genre titles add their minutes to each genre, so genre totals overlap.",
    ),
    (
        "complex",
        "q07-completion-vs-rating",
        "What is the completion rate of each movie, with average rating?",
        "For each movie, aggregate its watch events and independently average its reviews. An unwatched movie has no completion percentage.",
        "Many completed flags use the same MovieLens ratings as the reviews. The association is built into the seed and cannot show causation.",
    ),
    (
        "complex",
        "q08-binge-watchers",
        "Which users binge-watched (3 or more episodes of one series on one day)?",
        "Group completed series sessions by user, series, and the user's local calendar day. Count distinct episodes, then show up to 25 qualifying groups.",
        "Replays do not count as new episodes. This query shows at most 25 synthetic binge groups, not every qualifying group.",
    ),
    (
        "complex",
        "q09-revenue-and-churn",
        "What is the monthly revenue and churn per plan?",
        "Group generated payments by UTC payment month and plan. Divide current-plan cancellations that month by users active at its start.",
        "The output covers months with payments. It describes generated billing, not audited revenue. A current subscription snapshot cannot track all past plan changes.",
    ),
    (
        "complex",
        "q10-device-usage-by-hour",
        "How does device usage change by hour of day?",
        "Group events and watch minutes by user-local hour and device. Show six-hour dayparts and each device's cumulative hourly event share.",
        "Devices are assigned by the generator, and many hours come from rating timestamps. This result cannot establish real hourly demand.",
    ),
]

REFERENCES = [
    'Bingeling project, "Domain analysis," docs/domain-analysis.md, 2026.',
    'Bingeling project, "Data model," docs/data-model.md, 2026.',
    'Bingeling project, "Fixed questions," docs/questions.md, 2026.',
    'Bingeling project, "Guidelines," GUIDELINES.md, 2026.',
    'Netflix, "What we watched: The second half of 2025." [Online]. Available: https://about.netflix.com/news/what-we-watched-the-second-half-of-2025',
    'FICCI and EY, "India\'s media and entertainment sector in 2025," EY India newsroom, Mar. 2026. [Online]. Available: https://www.ey.com/en_in/newsroom/2026/03/india-s-media-and-entertainment-sector-grew-9-percent-to-inr-2-point-78-trillion-in-2025-driven-by-digital-and-live-experiences-ficci-ey-report',
    'Government of India, Press Information Bureau, "Video subscription revenue in 2024." [Online]. Available: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2205233&lang=2&reg=3',
    'MongoDB, Inc., "Data modeling best practices," MongoDB Docs. [Online]. Available: https://www.mongodb.com/docs/manual/data-modeling/best-practices/',
    'MongoDB, Inc., "Unbounded arrays anti-pattern," MongoDB Docs. [Online]. Available: https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/unbounded-arrays/',
    'MongoDB, Inc., "SonyLIV improves CMS performance by 98 percent on Atlas." [Online]. Available: https://www.mongodb.com/company/blog/innovation/sonyliv-improves-cms-performance-by-98-percent-on-atlas',
    'IMDb, "IMDb non-commercial datasets." [Online]. Available: https://data.imdb.com/non-commercial-datasets/',
    'GroupLens, "MovieLens 32M README and licence." [Online]. Available: https://files.grouplens.org/datasets/movielens/ml-32m-README.html',
    'Kaggle, "Netflix movies and TV shows," dataset metadata. [Online]. Available: https://www.kaggle.com/api/v1/datasets/view/shivamb/netflix-shows',
    'Deccan Chronicle, "ZEE5 clocks 105 billion watch minutes in FY25." [Online]. Available: https://www.deccanchronicle.com/entertainment/ott/zee5-clocks-105-billion-watch-minutes-in-fy25-amid-renewed-regional-push-1898817',
    'F. M. Harper and J. A. Konstan, "The MovieLens datasets: History and context," ACM Trans. Interact. Intell. Syst., vol. 5, no. 4, Art. no. 19, 2015, doi: 10.1145/2827872.',
]


def ieee_citations(text):
    """Turn internal [R12, R15] and [R1–R4] markers into IEEE numeric citations."""

    def replace(match):
        inner = match.group(1)
        numbers = re.findall(r"R(\d+)", inner)
        if "–" in inner:
            return f"[{numbers[0]}]–[{numbers[-1]}]"
        return ", ".join(f"[{number}]" for number in numbers)

    return re.sub(r"\[(R\d+(?:(?:–|,\s*)R\d+)*)\]", replace, text)


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
        raise ValueError(
            f"Screenshot is too small to show command and output: {path.relative_to(ROOT)}"
        )


def load_inputs():
    for name in ("report-outline.md", "domain-analysis.md", "data-model.md", "questions.md"):
        required(ROOT / "docs" / name)
    manifest = json.loads(required(DATA / "manifest.json").read_text(encoding="utf-8"))
    for field in ("demoUserId", "demoActor"):
        if not manifest.get(field):
            raise ValueError(f"data/manifest.json lacks {field}")
    collections = {}
    for name in ("users", "titles", "watch_events", "reviews", "plans", "payments"):
        path = required(DATA / f"{name}.json")
        collection = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(collection, list) or not collection:
            raise ValueError(f"data/{name}.json must contain a nonempty JSON array")
        recorded = manifest.get("files", {}).get(name, {})
        if recorded.get("count") != len(collection) or recorded.get("sha256") != sha256_file(path):
            raise ValueError(f"data/{name}.json differs from its manifest count or SHA-256")
        collections[name] = collection
    queries = []
    for group, stem, question, explanation, insight in QUESTIONS:
        query_path = required(ROOT / "queries" / group / f"{stem}.js")
        output_path = required(OUTPUT / f"{stem}.txt")
        screenshot_path = SCREENSHOTS / f"{stem}.png"
        image_is_png(screenshot_path)
        query = query_path.read_text(encoding="utf-8")
        output = output_path.read_text(encoding="utf-8")
        expected = f"queries/{group}/{stem}.js"
        if expected not in output.splitlines()[0]:
            raise ValueError(f"Saved output lacks query command for {expected}")
        if not query.strip() or not any(line.strip() for line in output.splitlines()[1:]):
            raise ValueError(f"Query or saved result is empty: {stem}")
        queries.append((group, stem, question, explanation, insight, query, output))
    return manifest, collections, queries


def compact_sample(document):
    # One line per document. Field values stay exactly as stored.
    return json.dumps(document, ensure_ascii=False)


def output_excerpt(text, stem, maximum=42):
    lines = text.rstrip().splitlines()
    excerpt = "\n".join(lines[:maximum])
    if len(lines) > maximum:
        excerpt += f"\n[Excerpt ends after {maximum} of {len(lines)} lines. Full saved output: docs/query-output/{stem}.txt]"
    return excerpt


def build(manifest, collections, queries):
    def n(collection):
        return f"{len(collections[collection]):,}"

    origins = Counter(
        str(item.get("source", {}).get("dataset", "not labelled")) for item in collections["titles"]
    )
    event_origins = Counter(
        str(item.get("origin", "not labelled")) for item in collections["watch_events"]
    )
    parts = [
        "```{=typst}\n",
        '#set heading(numbering: "1.")\n',
        '#set page(margin: (x: 1.6cm, y: 1.5cm), numbering: "1")\n',
        "#set text(size: 9pt)\n",
        "#set par(leading: 0.5em, spacing: 0.7em)\n",
        "#show raw: set text(size: 6.5pt)\n",
        "#show heading: set block(above: 0.9em, below: 0.5em)\n",
        "#align(center)[\n",
        "  #v(22%)\n",
        '  #text(size: 30pt, weight: "bold")[Bingeling]\n',
        "  #v(1cm)\n",
        "  #text(size: 18pt)[MongoDB Video Streaming Case Study]\n",
        "  #v(2cm)\n",
        "  #text(size: 16pt)[24BDS0367 Upayan Mazumder]\n",
        "  #v(1cm)\n",
        "  #text(size: 12pt)[CSE302L Database Systems]\n",
        "  #v(1cm)\n",
        "  #text(size: 12pt)[22 October 2026]\n",
        "]\n",
        "#pagebreak()\n",
        "#outline(title: [Contents], depth: 2)\n",
        "```\n\n",
        "# Introduction\n\n",
        "Bingeling models a video streaming service with MongoDB 7. It stores catalogue titles, user subscriptions, rating-derived viewing proxies, reviews, plans, and generated payments. This course case study uses published catalogue and rating records where marked. It does not operate a real streaming service. The objective is to answer five simple and five complex database questions with reproducible queries and captured results [R1–R4].\n\n",
        "# Domain analysis\n\n",
        "Video services need catalogue discovery, viewing history, subscriber state, and billing records. Subscribers need recent sessions. Content teams need viewing measures by title and region. Finance needs dated payments and cancellations. Product teams need completion and device-use measures [R1].\n\n",
        "Market figures have different definitions. The Government of India reported INR 9,200 crore in Indian video subscription revenue for 2024, citing FICCI-EY [R7]. FICCI-EY counted 216 million paid video subscriptions across 143 million households in 2025 [R6]. These are market context, not measurements of Bingeling. Netflix reported 96 billion viewing hours for July–December 2025. That figure covers Netflix, not this dataset [R5].\n\n",
        "ZEE5 reported 105 billion watch minutes in FY25 and said connected devices supplied 64% of premium-content watch time. These figures describe ZEE5, not all Indian viewers [R14].\n\n",
        "Streaming services can earn from subscriptions, ads, rentals, or combinations. This model covers subscriptions and simulated payments. Its watch events are rating-based viewing proxies or explicit synthetic scenarios, not observed video plays. It stores no video files or streaming bandwidth. The source distributions in [R1] describe IMDb metadata, not an Indian platform sample.\n\n",
        "# Choice of database\n\n",
        "MongoDB documents hold each title with its genres, cast, and bounded seasons. A title page can read these fields together. A user document holds a small profile list and the current subscription. MongoDB also supports aggregation pipelines for joins, time grouping, and ranking [R8]. SonyLIV reported improved content-management search after its move to MongoDB Atlas. That vendor case study concerns a content system. It does not prove that MongoDB serves video bytes [R10].\n\n",
        "Reference the growing `watch_events`, `reviews`, and `payments` collections rather than embedding them in users or titles. Embedded unbounded histories would grow documents and could hit the 16 MB BSON limit [R9]. The copied `watch_events.titleName` aids display but becomes stale if a title changes name. Cross-document joins and updates cost work. A relational database could enforce more relationships with foreign keys. MongoDB is a fit for this course catalogue and event analysis, not a claim of universal superiority [R1, R2, R8].\n\n",
        "# Data model\n\n",
        "The database is `bingeling`. Each document uses `_id`. Referenced IDs are BSON `ObjectId` values in Extended JSON seed files. Timestamps are BSON dates encoded as Extended JSON `$date`. The six collections are:\n\n",
        "| Collection | Role | Main relationships |\n|---|---|---|\n",
        "| `users` | Generated identities, country, current subscription | `_id` joins events, reviews, payments |\n",
        "| `titles` | Movies and series, cast and catalogue metadata | `_id` joins events and reviews |\n",
        "| `watch_events` | One generated viewing session per document | `userId`, `titleId`; copied `titleName` |\n",
        "| `reviews` | Selected MovieLens rating records, with empty text | `userId`, `titleId` |\n",
        "| `plans` | Plan price in INR | Plan key joins users and payments |\n",
        "| `payments` | Generated billing period and paid amount | `userId`, plan key |\n\n",
        "Movies have `runtimeMin`. Series have `seasons[].episodes[]` with episode runtimes. Events can identify a season and episode. Plans store `priceInr`; payment records store `amountInr`, `paidAt`, `periodStart`, and `periodEnd`. A payment is a generated record, not proof of a real transfer. The model embeds bounded title details and a user's current subscription. It references growing session, review, and payment histories [R2].\n\n",
        "The loader runs `scripts/schema.js`, which installs schema validators and indexes after import. Its indexes include unique `users.email`, `titles` by genre and release year, text search over title and cast names, `watch_events` by user and start time and by title, unique `(titleId, userId)` reviews, and payment indexes by plan or user and period start. These index definitions support the access patterns; this report does not claim measured speedups.\n\n",
        "## Sample seed documents\n\n",
        "The following examples come directly from the JSON arrays. The examples show stored types and field names, not a separate hand-written schema.\n\n",
    ]
    for name in ("users", "titles", "watch_events", "reviews", "plans", "payments"):
        parts += [f"### `{name}`\n\n", code(compact_sample(collections[name][0]), "json"), "\n"]
    parts += [
        "# Data population\n\n",
        "The checked-in arrays contain the following actual record counts at report-build time. Counts come from `data/<collection>.json`; they are not market estimates.\n\n",
        "| Collection | Records |\n|---|---:|\n",
    ]
    for name in ("users", "titles", "watch_events", "reviews", "plans", "payments"):
        parts.append(f"| `{name}` | {n(name)} |\n")
    parts += ["\n| Source archive | SHA-256 from manifest |\n|---|---|\n"]
    for name, source in sorted(manifest["sources"].items()):
        parts.append(f"| `{name}` | `{source['sha256']}` |\n")
    parts += [
        "\nThe generator in `scripts/generate_data.py` uses fixed seed `",
        str(manifest["seed"]),
        "`. It selects 400 Netflix-listed movies matched to MovieLens links and 100 Netflix-listed series. The source archives and SHA-256 values are in `data/manifest.json`. The loader imports the Extended JSON arrays and applies validators and indexes. MovieLens anonymous rating IDs link synthetic user names to selected title ratings. Review scores and timestamps come from MovieLens, while review text is empty. Many watch-event timestamps come from those ratings and are **not** observed watch starts. The script converts rating at least 3 into `completed` and a full movie runtime. It converts a lower rating into a half-runtime session. Other events, series episodes, languages inferred from country, devices, subscriptions, and payments are generated. Actor names and catalogue labels come from Netflix metadata [R11–R13].\n\n",
        "The Netflix titles source is a September 2021 CC0 snapshot [R13]. MovieLens 32M was generated in October 2023. It includes anonymous ratings, not demographics or watch logs [R12]. GroupLens permits research use and transformed redistribution only under its stated terms. It requires attribution and prohibits commercial or revenue-bearing use without permission. Those terms also apply to this derived seed data. This report does not imply GroupLens or University of Minnesota endorsement [R12, R15].\n\n",
        "Title source labels: ",
        ", ".join(f"`{key}`: {value:,}" for key, value in sorted(origins.items())),
        ". Watch-event origin labels: ",
        ", ".join(f"`{key}`: {value:,}" for key, value in sorted(event_origins.items())),
        ". The source archives are not an up-to-date full platform inventory. Neither a MovieLens rating nor a linked user ID proves that anyone watched a title on Bingeling.\n\n",
        "The fixed demo user has ObjectId `",
        str(manifest["demoUserId"]),
        "`. The fixed demo actor is `",
        str(manifest["demoActor"]),
        "`. These values are selection anchors, not real customer identities. The population screenshot below shows a captured terminal count command and its result.\n\n",
    ]
    image_is_png(SCREENSHOTS / "population.png")
    parts += [
        "![Population command and database counts](../screenshots/population.png){ width=70% }\n\n"
    ]
    for group, heading in (("simple", "Simple questions"), ("complex", "Complex questions")):
        parts += [
            f"# {heading}\n\n",
            "For every question, the JavaScript block below is copied directly from the named query file at build time. The terminal excerpt comes from the saved output. The PNG is a captured command-and-output image. The full saved output is in `docs/query-output/`. No query result is simulated in this report.\n\n",
        ]
        for query_group, stem, question, explanation, insight, query, output in queries:
            if query_group != group:
                continue
            number = int(stem[1:3])
            parts += [
                f"## Q{number}: {question}\n\n",
                "**Explanation.** ",
                explanation,
                "\n\n",
                f"**Query source:** `queries/{group}/{stem}.js`\n\n",
                code(query, "javascript"),
                "\n",
                f"Output file: `docs/query-output/{stem}.txt`. The screenshot shows the command and the output.\n\n",
                f"![Q{number} captured command and output](../screenshots/{stem}.png){{ width=70% }}\n\n",
                "**Insight and scope.** ",
                insight,
                " The screenshot above contains the observed records.\n\n",
            ]
    parts += [
        "# Insights\n\n",
        "The catalogue queries show available titles, languages, and cast matches. Country-genre minutes, completion, binge groups, and hourly device use are properties of this constructed dataset. They are not market demand estimates. Multi-genre titles appear in several genre totals. Completion and rating are linked by the generator's rating threshold, so their association is partly built into the data. Likewise, the generator assigns countries, devices, and plan states. Monthly payments are simulated. The saved outputs above give the exact result values for each query, subject to its stated scope.\n\n",
        "# Conclusion and limitations\n\n",
        "This case study demonstrates document modeling, indexed lookup designs, aggregation, and a repeatable source-to-report trail. Every query block comes from its executable source. Each screenshot shows a terminal run of its query file. Each numbered screenshot is required at build time. These checks prevent a report with missing evidence, but they cannot prove a screenshot came from a specific database state.\n\n",
        "Netflix catalogue labels are a dated sample. MovieLens ratings are not viewing logs [R12, R13]. User identities, country and time zone, devices, episodes, subscriptions, and payments are constructed. The generator derives many completion flags from ratings; this prevents independent inference from the Q7 comparison. A rating timestamp is not a watch-start time; Q4, Q8, and Q10 illustrate query mechanics rather than real viewing rhythms. A current subscription record cannot reconstruct all past plan changes. Payments do not prove collected or recognized revenue. Do not use these results for forecasts. Source terms restrict reuse of the MovieLens-derived records [R1, R12, R15].\n\n",
        "# References\n\n",
    ]
    for number, entry in enumerate(REFERENCES, start=1):
        suffix = " Accessed: Oct. 22, 2026." if "[Online]" in entry else ""
        parts += [f"- [{number}] {entry}{suffix}\n"]
    parts += [
        "\n**Evidence files:** `data/manifest.json`, the six `data/*.json` arrays, ten `queries/**/*.js` files, ten `docs/query-output/*.txt` files, and ten matching `screenshots/*.png`. These files fix the reproducible scope of this report.\n"
    ]
    return ieee_citations("".join(parts))


def main():
    try:
        manifest, collections, queries = load_inputs()
        REPORT.write_text(build(manifest, collections, queries), encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Cannot build report: {error}", file=sys.stderr)
        return 1
    print(f"Generated {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
