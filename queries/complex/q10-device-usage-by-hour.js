// Q10: How does device usage change by hour of day?
// Intent: Compare local-hour device use, daypart totals, and each device's cumulative
// share of its own daily-profile events as hours advance (not chronological dates).
// Collections: watch_events, users (IANA timezone per user).
const usage = db.watch_events
  .aggregate([
    { $lookup: { from: 'users', localField: 'userId', foreignField: '_id', as: 'user' } },
    { $unwind: '$user' },
    { $set: { localHour: { $hour: { date: '$startedAt', timezone: '$user.timezone' } } } },
    {
      $facet: {
        hourlyByDevice: [
          {
            $group: {
              _id: { device: '$device', hour: '$localHour' },
              events: { $sum: 1 },
              minutesWatched: { $sum: '$minutesWatched' }
            }
          },
          {
            $setWindowFields: {
              partitionBy: '$_id.device',
              sortBy: { '_id.hour': 1 },
              output: {
                runningEvents: { $sum: '$events', window: { documents: ['unbounded', 'current'] } },
                deviceEvents: { $sum: '$events', window: { documents: ['unbounded', 'unbounded'] } }
              }
            }
          },
          {
            $project: {
              _id: 0,
              device: '$_id.device',
              hour: '$_id.hour',
              events: 1,
              minutesWatched: 1,
              runningEvents: 1,
              runningSharePct: {
                $round: [{ $multiply: [{ $divide: ['$runningEvents', '$deviceEvents'] }, 100] }, 2]
              }
            }
          },
          { $sort: { hour: 1, device: 1 } }
        ],
        dayparts: [
          {
            $bucket: {
              groupBy: '$localHour',
              boundaries: [0, 6, 12, 18, 24],
              output: { events: { $sum: 1 }, minutesWatched: { $sum: '$minutesWatched' } }
            }
          },
          {
            $project: {
              _id: 0,
              startHour: '$_id',
              daypart: {
                $switch: {
                  branches: [
                    { case: { $eq: ['$_id', 0] }, then: 'night (00–06)' },
                    { case: { $eq: ['$_id', 6] }, then: 'morning (06–12)' },
                    { case: { $eq: ['$_id', 12] }, then: 'afternoon (12–18)' }
                  ],
                  default: 'evening (18–24)'
                }
              },
              events: 1,
              minutesWatched: 1
            }
          }
        ]
      }
    }
  ])
  .toArray()[0];
printjson({ hourlyDeviceRows: usage.hourlyByDevice.length, dayparts: usage.dayparts.length });
const byHour = new Map();
for (const row of usage.hourlyByDevice) {
  if (!byHour.has(row.hour)) byHour.set(row.hour, []);
  byHour.get(row.hour).push(row);
}
for (const [hour, devices] of byHour) printjson(EJSON.stringify({ hour, devices }));
usage.dayparts.forEach((row) => printjson(EJSON.stringify(row)));
