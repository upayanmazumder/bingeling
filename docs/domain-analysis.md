# Domain Analysis — Video Streaming Platform

## 1. Overview

A subscription video-on-demand (SVOD) platform gives users access to a catalogue of movies and series. Users pay a monthly fee for a plan. The platform records what each user watches. It uses this data for recommendations, content licensing, and pricing.

## 2. Stakeholders

| Stakeholder | Need from the data |
|-------------|--------------------|
| Subscribers | Search the catalogue, continue watching, get recommendations |
| Content team | Know which titles and genres perform well |
| Finance | Revenue by plan and region, churn |
| Product | Engagement, binge behaviour, device usage |
| Studios and licensors | Viewership numbers for their titles |

## 3. Entities

- **User** — account, region, plan, profiles, devices.
- **Title** — a movie or a series. Has genres, cast, language, release year, maturity rating.
- **Episode** — part of a series. Embedded in the series document.
- **Subscription** — plan, price, start date, end date, status.
- **Watch event** — one viewing session: user, title, episode, device, start time, minutes watched, completed flag.
- **Review** — user rating (1–5) and optional text for a title.

## 4. Why NoSQL (MongoDB)

- **Flexible schema.** Movies and series have different fields. One `titles` collection holds both.
- **Embedding.** Cast, genres, and episodes are read with the title. Embedding removes joins on the hot read path.
- **Write volume.** Watch events are append-only and numerous. MongoDB scales these writes with sharding on `userId`.
- **Aggregation.** The aggregation pipeline answers analytics questions inside the database.

## 5. Trade-offs

- Embedded data can be duplicated. Example: the title name is copied into watch events for fast reads. An update of a title name must update the copies.
- Multi-document transactions are possible, but slower. The design avoids them on the main paths.
- Unbounded arrays are a risk. Watch events are therefore a separate collection and not embedded in users.

## 6. Insights the case study targets

- Most-watched genres per region.
- Completion rate per title.
- Users who binge (3 or more episodes of one series in one day).
- Monthly revenue and churn per plan.
- Correlation between ratings and watch time.
