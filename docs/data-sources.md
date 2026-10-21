# Data Sources and Use Limits

The seed joins two public source archives. The script downloads the archives to `data/raw/`. Git ignores this directory. Commit only the small, transformed `data/*.json` seed files. Do not commit either raw archive.

| Source | Download | Data used | Use limit |
|---|---|---|---|
| [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows), September 2021 snapshot | [Kaggle dataset archive](https://www.kaggle.com/api/v1/datasets/download/shivamb/netflix-shows) | Title, type, release year, catalogue category, cast, duration, maturity | [Kaggle metadata](https://www.kaggle.com/api/v1/datasets/view/shivamb/netflix-shows) lists CC0. This is a 2021 snapshot, not a current Netflix catalogue. |
| [MovieLens 32M](https://grouplens.org/datasets/movielens/32m/), ratings through October 2023 | [GroupLens archive](https://files.grouplens.org/datasets/movielens/ml-32m.zip) | Anonymous user and movie IDs, individual rating, UTC rating timestamp, movie-to-IMDb ID link | [GroupLens licence and citation](https://files.grouplens.org/datasets/movielens/ml-32m-README.html). Research use requires attribution. No commercial use without permission. Redistribute transformations only under the same conditions. |

Cite MovieLens as: F. Maxwell Harper and Joseph A. Konstan, “The MovieLens Datasets: History and Context,” *ACM Transactions on Interactive Intelligent Systems* 5(4), 2015, [doi:10.1145/2827872](https://doi.org/10.1145/2827872). This project does not imply support from GroupLens or the University of Minnesota.

The generator matches movie names **and release years** across the two sources. It uses MovieLens `links.csv` to add IMDb IDs where available. This link is an identifier, not IMDb content. A title match can be wrong when different films share a name and year. The project makes no claim that MovieLens users watched the title on Netflix.

A MovieLens timestamp records a **rating**, not playback. An event with `origin: "movielens-rating-proxy"` keeps that real timestamp, anonymous user ID, movie ID, and rating (`sourceRating`). It does not represent a measured watch session. Its device and minutes are synthetic. `completed` uses the illustrative rule `sourceRating >= 3`. Reviews with `origin: "movielens-rating"` keep the actual rating value and timestamp. Review text is empty. The Netflix archive has no original audio language. `language` is a synthetic country-based proxy, and `languageOrigin` marks it. Episode lists and runtimes are synthetic, and `episodeOrigin` marks them. Payments, subscriber attributes, geography, names, and email addresses are synthetic.

`data/manifest.json` records both archive SHA-256 sums, each generated file's SHA-256, document counts, provenance totals, and demo anchors. The generator checks the Netflix archive SHA-256 and [GroupLens's published MD5](https://files.grouplens.org/datasets/movielens/ml-32m.zip.md5) before it writes output. It does not contain secrets or real addresses. User email addresses end in the reserved `example.com` domain. The numeric `sourceUserId` is an anonymous MovieLens ID. It is not a person's name or contact detail.
