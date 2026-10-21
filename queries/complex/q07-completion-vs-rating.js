// Q7: What is the completion rate of each movie, with average rating?
// Intent: Count completed movie watches and independently average title reviews (no fan-out).
// Collections: titles, watch_events, reviews.
const movies = db.titles
  .aggregate([
    { $match: { type: 'movie' } },
    {
      $lookup: {
        from: 'watch_events',
        let: { titleId: '$_id' },
        pipeline: [
          { $match: { $expr: { $eq: ['$titleId', '$$titleId'] } } },
          {
            $group: {
              _id: null,
              watches: { $sum: 1 },
              completedWatches: { $sum: { $cond: ['$completed', 1, 0] } }
            }
          }
        ],
        as: 'watchStats'
      }
    },
    {
      $lookup: {
        from: 'reviews',
        let: { titleId: '$_id' },
        pipeline: [
          { $match: { $expr: { $eq: ['$titleId', '$$titleId'] } } },
          { $group: { _id: null, averageRating: { $avg: '$rating' }, reviewCount: { $sum: 1 } } }
        ],
        as: 'reviewStats'
      }
    },
    {
      $set: {
        watchStats: { $first: '$watchStats' },
        reviewStats: { $first: '$reviewStats' }
      }
    },
    {
      $project: {
        _id: 0,
        title: '$name',
        releaseYear: 1,
        watches: { $ifNull: ['$watchStats.watches', 0] },
        completedWatches: { $ifNull: ['$watchStats.completedWatches', 0] },
        completionRatePct: {
          $cond: [
            { $gt: ['$watchStats.watches', 0] },
            {
              $round: [
                {
                  $multiply: [
                    { $divide: ['$watchStats.completedWatches', '$watchStats.watches'] },
                    100
                  ]
                },
                2
              ]
            },
            null
          ]
        },
        reviewCount: { $ifNull: ['$reviewStats.reviewCount', 0] },
        averageRating: { $round: ['$reviewStats.averageRating', 2] }
      }
    },
    { $sort: { completionRatePct: -1, title: 1 } }
  ])
  .toArray();
printjson({ totalMovies: movies.length, showingFirst: Math.min(20, movies.length) });
movies.slice(0, 20).forEach((row) => printjson(EJSON.stringify(row)));
