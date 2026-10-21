# Domain Analysis — Video Streaming Platform

This case study models an Indian video streaming service in MongoDB. It uses published market data and real-first source records. Generated fields remain labelled.

## 1. Industry overview

**Market size.** These figures describe different markets. Do not add them together.

| Measure | Period | Value | Source |
|---|---|---:|---|
| Global subscription video on demand (SVOD) revenue, forecast | 2026 | US$98.37 billion | [Statista](https://www.statista.com/outlook/amo/media/tv-video/ott-video/video-streaming-svod/worldwide/) |
| Global SVOD revenue growth, forecast | 2026–2031 | 5.72% compound annual growth rate | [Statista](https://www.statista.com/outlook/amo/media/tv-video/ott-video/video-streaming-svod/worldwide/) |
| India video subscription revenue | 2024 | ₹9,200 crore, up 11% | [Government of India, citing FICCI-EY](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2205233&lang=2&reg=3) |
| India video subscription revenue | 2025 | ₹14,800 crore, up 61% | [Fortune India, citing FICCI-EY](https://www.fortuneindia.com/business-news/ott-drives-digital-boom-subscriptions-surge-by-60-video-revenues-crosses-14800-cr-mark/131553) |
| India paid video subscriptions | 2025 | 216 million across 143 million households | [FICCI-EY](https://www.ey.com/en_in/newsroom/2026/03/india-s-media-and-entertainment-sector-grew-9-percent-to-inr-2-point-78-trillion-in-2025-driven-by-digital-and-live-experiences-ficci-ey-report) |
| India active paid OTT subscriptions | 2026 | 172.6 million, up 16% | [MediaNews4U, citing Ormax](https://www.medianews4u.com/indias-ott-universe-reaches-665-million-paid-subscriptions-rise-16-ctv-audience-jumps-60-ormax-report/) |

Statista excludes ad-only and pay-per-view services from SVOD. FICCI-EY and Ormax use different subscription measures. Ormax counts bundled access and defines an OTT viewer as anyone who watched online video in the previous month. Its 2026 estimate is 664.9 million OTT viewers, not 664.9 million paying subscribers ([Statista](https://www.statista.com/outlook/amo/media/tv-video/ott-video/video-streaming-svod/worldwide/), [Ormax via MediaNews4U](https://www.medianews4u.com/indias-ott-universe-reaches-665-million-paid-subscriptions-rise-16-ctv-audience-jumps-60-ormax-report/)).

**Players.** Netflix crossed 325 million global paid memberships in Q4 2025 ([Netflix shareholder letter](https://s22.q4cdn.com/959853165/files/doc_financials/2025/q4/FINAL-Q4-25-Shareholder-Letter.pdf)). JioHotstar reported 280 million subscribers in May 2025 ([Business Standard](https://www.business-standard.com/companies/news/jiohotstar-second-to-netflix-with-280-million-subscribers-125052701396_1.html)). Another report counted 100 million in March 2025 ([Variety](https://variety.com/2025/tv/news/india-jiohotstar-100-million-subscribers-1236349614/)). The dates and definitions differ. Neither count is a comparable Netflix global figure. JustWatch's Q2 2025 *India platform share* was JioHotstar 25%, Prime Video 23%, Netflix 19%, Apple TV+ 14%, ZEE5 10%, SonyLIV 5%, and others 4%. These are shares reported by a streaming guide, **not subscriber counts** ([MediaNews4U](https://www.medianews4u.com/indias-svod-market-share-q2-2025/)).

| Model | Income | Example and evidence |
|---|---|---|
| SVOD | Recurring access fee | Netflix's paid memberships ([Netflix](https://s22.q4cdn.com/959853165/files/doc_financials/2025/q4/FINAL-Q4-25-Shareholder-Letter.pdf)) |
| AVOD | Ads pay for free viewing | Amazon MX Player ([Variety](https://variety.com/2025/tv/news/amazon-india-streaming-prime-video-mx-player-1236441219/)) |
| TVOD | Customer rents or buys one title | Prime Video Store in India ([Amazon](https://press.aboutamazon.com/in/2022/4/amazon-prime-video-bets-big-on-india-announces-its-biggest-content-slate-of-series-movies-and-co-productions-across-genres-and-languages)) |
| Hybrid | Subscription and advertising | Prime Video added limited ads in India ([Economic Times](https://m.economictimes.com/industry/media/entertainment/prime-video-to-introduce-limited-ads-in-india-from-june-17/articleshow/121156978.cms)) |

**India plan prices.** These are list prices reported in October 2026. Prices and features can change ([Gadgets Now](https://gadgetsnow.indiatimes.com/faqs/netflix-vs-jiohotstar-vs-prime-video-vs-sonyliv-which-ott-subscription-offers-the-most-benefits-in-october-2026/articleshow/135003304.cms)).

| Platform | Mobile-only | Basic or Super | Standard | Premium |
|---|---:|---:|---:|---:|
| Netflix, monthly | ₹149 | ₹199 | ₹499 | ₹649 |
| JioHotstar, monthly | ₹79 | ₹149 | — | ₹299 |
| JioHotstar, annual | ₹499 | ₹1,099 | — | ₹2,199 |
| SonyLIV | ₹699 yearly | — | — | ₹399 monthly or ₹1,499 yearly |

Netflix Mobile supports one phone or tablet. Netflix Basic, Standard, and Premium support one, two, and four simultaneous screens. JioHotstar Mobile, Super, and Premium support one, two, and four devices. JioHotstar Mobile requires an add-on for Hollywood titles ([Gadgets Now](https://gadgetsnow.indiatimes.com/faqs/netflix-vs-jiohotstar-vs-prime-video-vs-sonyliv-which-ott-subscription-offers-the-most-benefits-in-october-2026/articleshow/135003304.cms)). These prices describe the market. This project's `plans` collection can keep its own stated prices.

## 2. Stakeholders and their data needs

These decisions are design examples. Netflix says it uses engagement to assess retention. SonyLIV describes a content system that supports publishing and discovery ([Netflix](https://s22.q4cdn.com/959853165/files/doc_financials/2025/q4/FINAL-Q4-25-Shareholder-Letter.pdf), [MongoDB](https://www.mongodb.com/company/blog/innovation/sonyliv-improves-cms-performance-by-98-percent-on-atlas)).

| Stakeholder | Data needed | Decision |
|---|---|---|
| Subscribers | Profiles, device, viewing progress, plan | Resume a title or change plan |
| Content and licensing teams | Watch time by title, language, region, licence period | Renew a licence or commission a title |
| Finance | Payments, plan, refunds, cancellations | Price plans and forecast revenue |
| Product and growth teams | Session starts, completion, device, retention | Improve discovery or reduce cancellation |
| Studios and licensors | Agreed title-level viewing and contract terms | Assess a title's performance or negotiate rights |

## 3. Data generated by a platform

The collections follow [the project data model](data-model.md). `users` embeds profiles and current subscription state. `titles` embeds genres, cast, seasons, and episodes. `watch_events` stores one proxy viewing session per document. `reviews` stores a MovieLens rating and optional tag. `plans` stores prices. `payments` stores generated billing history. Device type is generated on each event. Several user countries permit comparisons.

| Scale indicator | Value and scope | Source |
|---|---|---|
| Netflix view hours | 96 billion in July–December 2025, about 522 million per day on average | [Netflix engagement report](https://about.netflix.com/news/what-we-watched-the-second-half-of-2025) |
| Netflix data pipeline | About 500 billion events daily in 2016, across services and event types | [Accessible summary of Netflix's engineering post](https://www.engineering.fyi/article/evolution-of-the-netflix-data-pipeline) |
| Netflix pipeline later | Described as trillions of events daily in 2018 | [Accessible summary of Netflix's Keystone post](https://www.engineering.fyi/article/keystone-real-time-stream-processing-platform) |
| Disney+ Hotstar viewing | About 1 billion minutes daily in 2022 | [ScyllaDB case study](https://www.scylladb.com/2022/06/28/why-disney-hotstar-replaced-redis-and-elasticsearch-with-scylladb-cloud/) |
| Project seed target | 500 titles, 2,000 users, 50,000 watch events, 5,000 reviews | [Project guidelines](../GUIDELINES.md) |

Pipeline events include more than play events. Watch hours do not equal event counts. The project seed target is a course design choice, not a reported platform volume.

| Metric | Case-study definition |
|---|---|
| Watch time | Sum of `minutesWatched` over events in the selected period |
| Completion rate | Events marked `completed`, divided by all started watch events |
| Churn | Accounts that cancel in a month divided by active accounts at the month's start |
| ARPU | Monthly recognised subscription revenue divided by average active paying accounts that month |
| Binge rate | Share of active series viewers with at least three distinct episodes of one series on one local calendar day |
| Device split | Watch minutes by `device`, divided by total watch minutes |

These are operational definitions, not universal standards. Count distinct episodes to avoid counting replays as binges. Historical ARPU and churn need past subscription states and payments. The current `users.subscription` snapshot alone cannot measure them reliably.

## 4. Why NoSQL for this domain

Netflix used Cassandra for viewing history. Its newer time-series service also uses Cassandra ([Netflix engineering](https://netflixtechblog.com/scaling-time-series-data-storage-part-i-ec2b6d44ba39), [Netflix engineering, 2026](https://netflixtechblog.com/dynamically-splitting-wide-partitions-in-cassandra-for-time-series-workloads-0eded064f456)). Disney+ Hotstar moved its Continue Watching data from Redis and Elasticsearch to ScyllaDB Cloud. The case study reports 100–200 GB of data daily for this feature ([ScyllaDB](https://www.scylladb.com/2022/06/28/why-disney-hotstar-replaced-redis-and-elasticsearch-with-scylladb-cloud/)). These cases show that platforms use different stores for different workloads. They do not prove that MongoDB alone can serve every workload.

SonyLIV moved its content management system from a relational database to MongoDB Atlas. The source reports about 495,000 documents and a search latency drop from 1.3 seconds to 0.022–0.030 seconds after optimization ([MongoDB customer story](https://www.mongodb.com/company/blog/innovation/sonyliv-improves-cms-performance-by-98-percent-on-atlas)). This supports MongoDB for a changing catalogue, not a claim that MongoDB streams video files.

A relational catalogue might have separate `titles`, `seasons`, `episodes`, `genres`, and `cast` tables. MongoDB can hold a movie or a series in one `titles` document. Embed the small fields read with a title, such as genres and bounded seasons. Reference `watch_events` and `reviews`, which grow without a fixed bound ([MongoDB data-model guidance](https://www.mongodb.com/docs/manual/data-modeling/best-practices/)). Keep episodes separate if a series becomes too large or episodes require independent, frequent updates.

Denormalisation makes reads simple but duplicates values. This project copies `titleName` into `watch_events`, so a rename can leave old events with stale names. A single MongoDB document update is atomic. Cross-document transactions have more cost. Unbounded arrays can reach MongoDB's 16 MB document limit and hurt index performance ([MongoDB data-model guidance](https://www.mongodb.com/docs/manual/data-modeling/best-practices/), [unbounded-array guidance](https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/unbounded-arrays/)). Do not embed watch history or all reviews in a user or title document.

## 5. Analytics and published insights

The [fixed project questions](questions.md) ask for top genres per country, completion versus rating, binge viewers, plan revenue and churn, and device usage by hour. These questions support catalogue decisions, product changes, and plan analysis. Revenue and churn need historical billing data before they can be reported as real measured results.

| Published observation | Use and limit |
|---|---|
| Netflix reported 96 billion hours in H2 2025. Non-English titles accounted for over one third of viewing. *KPop Demon Hunters* had 482 million views. | Compare language and title concentration, not country-level demand. Netflix defines a view as hours divided by runtime ([Netflix](https://about.netflix.com/news/what-we-watched-the-second-half-of-2025)). |
| ZEE5 reported 105 billion watch minutes in FY25. Drama accounted for over 40 billion. Connected devices supplied 64% of premium-content watch time. | Seed an India-focused scenario. These figures describe ZEE5, not all Indian platforms ([Deccan Chronicle](https://www.deccanchronicle.com/entertainment/ott/zee5-clocks-105-billion-watch-minutes-in-fy25-amid-renewed-regional-push-1898817)). |
| ZEE5 reported increased binge viewing from 5 PM to 11 PM. | This is platform-specific context. MovieLens timestamps are not Indian viewing times ([Deccan Chronicle](https://www.deccanchronicle.com/entertainment/ott/zee5-clocks-105-billion-watch-minutes-in-fy25-amid-renewed-regional-push-1898817)). |
| An Omdia survey reported annual churn above 10% for most surveyed Indian services in November 2021. Lack of content was a leading reason for online cancellations. | This is dated survey evidence. The survey covered online English-speaking respondents ([Exchange4media](https://www.exchange4media.com/digital-news/indias-the-only-market-where-average-resubscription-rates-are-above-churn-rates-report-119719.html)). |

## 6. Realistic data for seeding

| Dataset | Useful fields | Use terms |
|---|---|---|
| [Kaggle Netflix titles](https://www.kaggle.com/datasets/shivamb/netflix-shows) | Catalogue labels, genres, release dates | [Kaggle metadata](https://www.kaggle.com/api/v1/datasets/view/shivamb/netflix-shows) lists **CC0**. The data last changed in September 2021. Do not treat it as a current catalogue. |
| [IMDb non-commercial files](https://data.imdb.com/non-commercial-datasets/) | `title.basics` for genre and runtime, `title.episode` for episode links, `title.ratings` for title averages | Personal and non-commercial use under IMDb's terms. Files update daily. Do not publish raw IMDb data without checking its terms. |
| [MovieLens 32M](https://grouplens.org/datasets/movielens/) | 32 million individual ratings, movie links and genres | [README licence](https://files.grouplens.org/datasets/movielens/ml-32m-README.html): research use, attribution, no commercial use without permission. It permits redistribution on the same terms. Link to the original instead. |

**Measured source distributions.** We downloaded IMDb `title.basics.tsv.gz` and `title.ratings.tsv.gz` on 21 October 2026. We excluded adult titles. We selected `movie`, `tvSeries`, and `tvEpisode` by `titleType`. We counted a title once per listed genre. We kept runtimes from 1 to 999 minutes. We used only title averages with at least 1,000 votes for rating statistics. These counts describe IMDb, **not** an Indian streaming catalogue ([IMDb file definitions](https://data.imdb.com/non-commercial-datasets/)).

| Statistic | Movies | Series or episodes |
|---|---:|---:|
| Genre shares | Drama 36.9%, Documentary 20.2%, Comedy 16.7%, Action 8.3% | Series: Comedy 22.3%, Drama 19.4%, Documentary 12.6% |
| Runtime p25 / median / p75 | 73 / 89 / 100 minutes, 482,325 movies | Episode: 23 / 30 / 50 minutes, 3,044,440 episodes |
| Median IMDb title rating, at least 1,000 votes | 6.4 / 10, 49,318 movies | 7.3 / 10, 10,360 series |

Genre shares overlap because IMDb lists up to three genres per title. IMDb ratings are *title averages*. MovieLens supplies individual 0.5–5-star ratings ([IMDb](https://data.imdb.com/non-commercial-datasets/), [MovieLens README](https://files.grouplens.org/datasets/movielens/ml-32m-README.html)). Use real title and rating records where possible. Generate names, e-mail addresses, devices, subscriptions, and payments. A rating timestamp is a proxy, not a watch time. No public source records this service's subscriber behavior. Use a fixed seed and label each generated field.

### Insights to examine with MongoDB aggregations

1. **Genre demand varies by country.** Join `watch_events` to `titles` and `users`, then group watch minutes by country and genre. Seed more than one country.
2. **Some generated series sessions include three distinct episodes in one day.** Group distinct episodes by user, series, and local day.
3. **Completion varies by device.** Group completed and started events by device and title type.
4. **The device split changes by hour.** Group events by source timestamp and generated device. Do not infer India viewing habits.
5. **A few titles receive much of the watch time.** Group minutes by title, sort titles, and calculate cumulative share.
6. **Rating bands have different completion rates.** Join reviews and events by title. Compare bands without claiming causation.
7. **Current plans differ in watch time per account.** Join `watch_events` with users by `userId` and group by current plan. Do not describe this as historical plan use.

**Limitations and method.** Sources include company reports, vendor case studies, trade press, and IMDb files. Company and vendor reports describe their own services. Netflix's old engineering pages denied direct access, so accessible summaries support the historical pipeline counts. Market estimates use different definitions. Generated sessions and billing cannot show real market behaviour. AI-assisted tools helped search sources, compare claims, and calculate IMDb distributions.

**Source check.** On 22 October 2026, an automated request reached 25 of the 29 cited URLs (HTTP 200). A reachable page does not prove that it still shows the quoted figure. Four URLs returned HTTP 403 to the automated request: the Gadgets Now price comparison, two Netflix engineering posts, and the Exchange4media churn article. A browser may open them. The author must read these four pages before the report cites them as primary evidence. The report cites each source with this access date.
