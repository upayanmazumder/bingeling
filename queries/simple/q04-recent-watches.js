// Q4: Show the 10 most recent watch events of one user.
// Intent: Use the fixed demo user anchor and present their latest activity.
// Collections: watch_events; anchor from data/manifest.json.
const demoUserId = ObjectId(
  JSON.parse(require('fs').readFileSync('data/manifest.json', 'utf8')).demoUserId
);
printjson({ userId: demoUserId, showingNewest: 10 });
db.watch_events
  .find(
    { userId: demoUserId },
    {
      titleName: 1,
      titleId: 1,
      startedAt: 1,
      minutesWatched: 1,
      completed: 1,
      device: 1,
      season: 1,
      episode: 1,
      origin: 1
    }
  )
  .sort({ startedAt: -1, _id: -1 })
  .limit(10)
  .forEach((row) => printjson(EJSON.stringify(row)));
