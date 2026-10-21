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
