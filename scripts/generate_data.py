#!/usr/bin/env python3
"""Generate reproducible Bingeling seed arrays from local public source archives.

Download the two archives with --download. No raw dataset is copied to the output.
"""

import argparse
import csv
import hashlib
import io
import json
import random
import re
import unicodedata
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
SEED = 367
SOURCES = {
    "netflix-shows.zip": (
        "https://www.kaggle.com/api/v1/datasets/download/shivamb/netflix-shows",
        "1e5477bbbe868845be3b852d80eec2f1da6570340860668549a6dd5da0b00054",
    ),
    "ml-32m.zip": (
        "https://files.grouplens.org/datasets/movielens/ml-32m.zip",
        "e4a68655d7386b8f95f2f2424b2ff975dfdd15ffd59e0d864a14dca43e99d6ee",
    ),
}
MOVIELENS_MD5 = "d472be332d4daa821edc399621853b57"
COUNTRIES = (("IN", "Asia/Kolkata"), ("US", "America/New_York"),
             ("GB", "Europe/London"), ("CA", "America/Toronto"))
GENRES = {
    "Thrillers": "Thriller", "TV Thrillers": "Thriller", "Crime TV Shows": "Crime",
    "TV Mysteries": "Mystery", "TV Dramas": "Drama", "Dramas": "Drama",
    "TV Comedies": "Comedy", "Comedies": "Comedy", "TV Horror": "Horror",
    "Horror Movies": "Horror", "Action & Adventure": "Action",
    "TV Action & Adventure": "Action", "Romantic Movies": "Romance",
    "Romantic TV Shows": "Romance", "Documentaries": "Documentary",
    "Docuseries": "Documentary", "Sci-Fi & Fantasy": "Sci-Fi",
    "TV Sci-Fi & Fantasy": "Sci-Fi", "Children & Family Movies": "Family",
    "Kids' TV": "Family", "Music & Musicals": "Musical",
    "Classic Movies": "Classic", "Independent Movies": "Independent",
    "Anime Series": "Animation", "Anime Features": "Animation",
    "International Movies": "International", "International TV Shows": "International",
}
FIRST_NAMES = ("Aarav", "Aditi", "Isha", "Kabir", "Meera", "Neel", "Priya", "Rohan")
LAST_NAMES = ("Shah", "Rao", "Bose", "Singh", "Das", "Mehta", "Nair", "Kapoor")
DEVICES = ("tv", "mobile", "web", "tablet")
BASE = datetime(2023, 1, 1, tzinfo=timezone.utc)


def oid(kind, number):
    return {"$oid": f"{kind:02x}{number:022x}"}


def date(value):
    return {"$date": value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_sources(download):
    RAW.mkdir(parents=True, exist_ok=True)
    for filename, (url, expected) in SOURCES.items():
        path = RAW / filename
        if not path.exists():
            if not download:
                raise FileNotFoundError(f"Missing {path}; run python3 scripts/generate_data.py --download")
            pending = path.with_suffix(path.suffix + ".part")
            request = urllib.request.Request(url)
            if pending.exists():
                request.add_header("Range", f"bytes={pending.stat().st_size}-")
            with urllib.request.urlopen(request, timeout=120) as response:
                resumed = response.status == 206
                with pending.open("ab" if resumed else "wb") as out:
                    while chunk := response.read(1024 * 1024):
                        out.write(chunk)
            pending.replace(path)
        actual = sha256(path)
        if expected and actual != expected:
            raise ValueError(f"SHA-256 mismatch for {path}: {actual} != {expected}")
        if filename == "ml-32m.zip":
            md5 = hashlib.md5()
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    md5.update(chunk)
            if md5.hexdigest() != MOVIELENS_MD5:
                raise ValueError(f"GroupLens MD5 mismatch for {path}: {md5.hexdigest()}")


def csv_rows(archive, filename):
    with zipfile.ZipFile(archive) as bundle, bundle.open(filename) as source:
        yield from csv.DictReader(io.TextIOWrapper(source, encoding="utf-8-sig", newline=""))


def title_key(name):
    name = re.sub(r"\s*\(\d{4}\)$", "", name).strip()
    name = re.sub(r", (The|A|An)$", r"\1 ", name, flags=re.I)
    name = unicodedata.normalize("NFKD", name)
    return re.sub(r"[^a-z0-9]", "", name.lower())


def catalogue():
    rows = {}
    for row in csv_rows(RAW / "netflix-shows.zip", "netflix_titles.csv"):
        try:
            year = int(row["release_year"])
        except ValueError:
            continue
        if row["type"] not in ("Movie", "TV Show") or not row["title"].strip():
            continue
        key = (title_key(row["title"]), year)
        rows.setdefault(key, []).append(row)
    return rows


def movielens_matches(netflix):
    links = {}
    for row in csv_rows(RAW / "ml-32m.zip", "ml-32m/links.csv"):
        links[int(row["movieId"])] = row["imdbId"]
    result = {}
    for row in csv_rows(RAW / "ml-32m.zip", "ml-32m/movies.csv"):
        match = re.search(r"\((\d{4})\)$", row["title"])
        if not match:
            continue
        key = (title_key(row["title"]), int(match.group(1)))
        if key not in netflix:
            continue
        for nrow in netflix[key]:
            if nrow["type"] == "Movie":
                result.setdefault(int(row["movieId"]), (nrow, links.get(int(row["movieId"]), "")))
                break
    return result


def build_titles(netflix, matched, rng):
    # Favor highly rated linked films so source rows fill watch events without reuse.
    popularity = Counter()
    for rating in csv_rows(RAW / "ml-32m.zip", "ml-32m/ratings.csv"):
        movie = int(rating["movieId"])
        if movie in matched:
            popularity[movie] += 1
    movies = sorted(matched.items(), key=lambda pair: (-popularity[pair[0]], pair[0]))
    thrillers = [pair for pair in movies if int(pair[1][0]["release_year"]) > 2018
                 and "Thrillers" in pair[1][0]["listed_in"]]
    ordered = thrillers[:10] + movies
    chosen = []
    used = set()
    for mid, (row, imdb) in ordered:
        if len(chosen) == 400:
            break
        if row["show_id"] not in used:
            chosen.append((row, mid, imdb))
            used.add(row["show_id"])
    if len(chosen) < 400 or not thrillers:
        raise ValueError(f"Only {len(chosen)} linked movies; need at least 400 and recent thrillers")
    shows = sorted((row for rows in netflix.values() for row in rows
                    if row["type"] == "TV Show" and row["cast"].strip()),
                   key=lambda row: int(row["show_id"][1:]))[:100]
    if len(shows) < 100:
        raise ValueError("Need 100 Netflix series with public cast")
    chosen.extend((row, None, "") for row in shows)
    titles = []
    movie_ids = {}
    for row, mid, imdb in chosen:
        series = row["type"] == "TV Show"
        number = int(row["show_id"][1:])
        country = row["country"].lower()
        language = ("hi" if "india" in country else "ko" if "south korea" in country
                    else "ja" if "japan" in country else "es" if "spain" in country
                    else "en")
        categories = [GENRES.get(genre.strip(), genre.strip())
                      for genre in row["listed_in"].split(",") if genre.strip()]
        genres = list(dict.fromkeys(categories)) or ["Other"]
        maturity = "A" if row["rating"] in ("TV-MA", "R", "NC-17") else (
            "U" if row["rating"] in ("G", "TV-G", "TV-Y", "TV-Y7") else "UA")
        title = {"_id": oid(2, number), "type": "series" if series else "movie",
                 "name": row["title"], "releaseYear": int(row["release_year"]),
                 "productionCountries": [place.strip() for place in row["country"].split(",")
                                         if place.strip()],
                 "language": language, "languageOrigin": "synthetic-country-proxy",
                 "genres": genres, "maturity": maturity,
                 "maturityOrigin": "mapped-netflix-rating",
                 "cast": [{"name": name.strip()} for name in row["cast"].split(",") if name.strip()],
                 "source": {"dataset": "netflix-shows-2021", "showId": row["show_id"],
                            "netflixRating": row["rating"], "listedIn": row["listed_in"]}}
        if series:
            seasons_match = re.match(r"(\d+) Season", row["duration"])
            count = min(int(seasons_match.group(1)), 5) if seasons_match else 1
            title["seasons"] = [{"number": s, "episodes": [
                {"number": episode, "name": f"Episode {episode}", "runtimeMin": rng.randint(30, 55)}
                for episode in range(1, 7)]} for s in range(1, count + 1)]
            title["episodeOrigin"] = "synthetic: Netflix lists seasons, not episodes"
        else:
            runtime = re.match(r"(\d+) min", row["duration"])
            title["runtimeMin"] = int(runtime.group(1)) if runtime else 90
            if not runtime:
                title["runtimeOrigin"] = "synthetic-fallback"
            title["source"]["movieLensMovieId"] = mid
            if imdb:
                title["source"]["imdbId"] = "tt" + imdb.zfill(7)
            movie_ids[mid] = title
        titles.append(title)
    return titles, movie_ids


def rating_candidates(movie_ids):
    allowed = set(movie_ids)
    counts = Counter()
    archive = RAW / "ml-32m.zip"
    for row in csv_rows(archive, "ml-32m/ratings.csv"):
        if int(row["movieId"]) in allowed:
            counts[int(row["userId"])] += 1
    selected = {user for user, _ in counts.most_common(2000)}
    if len(selected) != 2000:
        raise ValueError(f"Only {len(selected)} source users match the catalogue")
    ratings = []
    for row in csv_rows(archive, "ml-32m/ratings.csv"):
        user = int(row["userId"])
        movie = int(row["movieId"])
        if user in selected and movie in allowed:
            ratings.append((user, movie, float(row["rating"]), int(row["timestamp"])))
    return selected, ratings


def write_json(name, documents):
    path = DATA / f"{name}.json"
    with path.open("w", encoding="utf-8") as output:
        json.dump(documents, output, ensure_ascii=False, separators=(",", ":"))
        output.write("\n")
    return {"count": len(documents), "sha256": sha256(path)}


def generate():
    rng = random.Random(SEED)
    netflix = catalogue()
    titles, movie_ids = build_titles(netflix, movielens_matches(netflix), rng)
    selected, ratings = rating_candidates(movie_ids)
    if len(ratings) < 5000:
        raise ValueError(f"Only {len(ratings)} matched ratings; need 5,000 real reviews")
    now = datetime(2026, 10, 1, tzinfo=timezone.utc)
    plans = [
        {"_id": name, "name": name, "priceInr": price, "screens": screens, "maxQuality": quality}
        for name, price, screens, quality in
        (("basic", 199, 1, "HD"), ("standard", 499, 2, "Full HD"),
         ("premium", 649, 4, "4K"))
    ]
    users = []
    payments = []
    user_ids = sorted(selected)
    for user in user_ids:
        plan = plans[user % 3]
        country, tz = COUNTRIES[user % len(COUNTRIES)]
        start = datetime(2025, 1 + user % 8, 1, tzinfo=timezone.utc)
        cancelled = user % 11 == 0
        ended = datetime(2026, 1 + user % 8, 1, tzinfo=timezone.utc) if cancelled else None
        users.append({"_id": oid(1, user), "sourceUserId": user,
                      "name": f"{FIRST_NAMES[user % 8]} {LAST_NAMES[(user // 8) % 8]}",
                      "email": f"bingeling-{user:06d}@example.com", "country": country,
                      "timezone": tz, "joinedAt": date(datetime(1990, 1, 1, tzinfo=timezone.utc)),
                      "profiles": [{"name": "Main", "kids": False}],
                      "subscription": {"plan": plan["name"],
                                       "status": "cancelled" if cancelled else "active",
                                       "startedAt": date(start),
                                       "endedAt": date(ended) if ended else None},
                      "identityOrigin": "synthetic; sourceUserId is anonymous MovieLens ID"})
        current = start
        while current < (ended or now):
            following = datetime(current.year + (current.month == 12),
                                 current.month % 12 + 1, 1, tzinfo=timezone.utc)
            payments.append({"_id": oid(5, len(payments) + 1), "userId": oid(1, user),
                             "plan": plan["name"], "amountInr": plan["priceInr"],
                             "paidAt": date(current), "periodStart": date(current),
                             "periodEnd": date(following), "origin": "synthetic"})
            current = following
    # A rating is not a viewing log. Preserve its UTC timestamp as a proxy.
    # Sample source rows without replacement; reviews preserve actual star values.
    rng.shuffle(ratings)
    reviews = []
    for user, movie, score, timestamp in ratings[:5000]:
        reviews.append({"_id": oid(4, len(reviews) + 1), "userId": oid(1, user),
                        "titleId": movie_ids[movie]["_id"], "rating": score,
                        "text": "", "createdAt": date(datetime.fromtimestamp(timestamp, timezone.utc)),
                        "origin": "movielens-rating", "sourceMovieId": movie})
    events = []
    for user, movie, score, timestamp in ratings[:50000]:
        title = movie_ids[movie]
        length = title["runtimeMin"]
        completed = score >= 3
        events.append({"_id": oid(3, len(events) + 1), "userId": oid(1, user),
                       "titleId": title["_id"], "titleName": title["name"],
                       "device": DEVICES[(user + movie) % len(DEVICES)],
                       "startedAt": date(datetime.fromtimestamp(timestamp, timezone.utc)),
                       "minutesWatched": length if completed else max(1, length // 2),
                       "completed": completed, "origin": "movielens-rating-proxy",
                       "sourceMovieId": movie, "sourceRating": score})
    # Only when source-linked events cannot fill the target, add labelled scenarios.
    while len(events) < 50000:
        user = user_ids[len(events) % len(user_ids)]
        title = titles[len(events) % len(titles)]
        episode = title["type"] == "series"
        length = title["seasons"][0]["episodes"][0]["runtimeMin"] if episode else title["runtimeMin"]
        event = {"_id": oid(3, len(events) + 1), "userId": oid(1, user),
                 "titleId": title["_id"], "titleName": title["name"],
                 "device": DEVICES[len(events) % 4],
                 "startedAt": date(BASE + timedelta(days=len(events) % 980,
                                                     hours=len(events) % 20)),
                 "minutesWatched": length, "completed": True, "origin": "synthetic"}
        if episode:
            event.update(season=1, episode=1)
        events.append(event)
    series = next(title for title in titles if title["type"] == "series")
    demo_user = user_ids[0]
    for episode in (1, 2, 3):
        events[-(4 - episode)] = {
            "_id": oid(3, 50000 - (4 - episode) + 1), "userId": oid(1, demo_user),
            "titleId": series["_id"], "titleName": series["name"],
            "season": 1, "episode": episode, "device": "tv",
            "startedAt": date(datetime(2023, 6, 12, 14 + episode, tzinfo=timezone.utc)),
            "minutesWatched": series["seasons"][0]["episodes"][episode - 1]["runtimeMin"],
            "completed": True, "origin": "synthetic-binge-scenario"}
    actor = next(person["name"] for title in titles if title["type"] == "movie"
                 and title["cast"] for person in title["cast"])
    files = {name: write_json(name, docs) for name, docs in (
        ("users", users), ("titles", titles), ("watch_events", events),
        ("reviews", reviews), ("plans", plans), ("payments", payments))}
    manifest = {"seed": SEED, "demoUserId": oid(1, demo_user)["$oid"],
                "demoActor": actor, "bingeTitleId": series["_id"]["$oid"],
                "sources": {filename: {"url": url, "sha256": sha256(RAW / filename)}
                            for filename, (url, _) in SOURCES.items()},
                "files": files,
                "provenance": {"realRatingProxyEvents": sum(
                    event["origin"] == "movielens-rating-proxy" for event in events),
                    "syntheticEvents": sum(event["origin"].startswith("synthetic") for event in events),
                    "realRatingReviews": len(reviews),
                    "matchedMovieTitles": len(movie_ids),
                    "netflixSeriesTitles": 100}}
    write_json("manifest", manifest)
    print(json.dumps({"files": files, "provenance": manifest["provenance"],
                      "demoUserId": manifest["demoUserId"], "demoActor": actor}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="fetch missing archives into data/raw")
    args = parser.parse_args()
    get_sources(args.download)
    generate()


if __name__ == "__main__":
    main()
