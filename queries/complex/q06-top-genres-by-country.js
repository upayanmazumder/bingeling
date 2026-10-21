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
