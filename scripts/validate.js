// Validate the imported seed and its local manifest. Run with mongosh bingeling scripts/validate.js.
const fs = require('fs');
const crypto = require('crypto');
const manifest = JSON.parse(fs.readFileSync('/workspace/data/manifest.json', 'utf8'));
function ensure(condition, message) {
  if (!condition) throw new Error(`Seed validation failed: ${message}`);
}
function missingReference(collection, target, field) {
  return db.getCollection(collection).aggregate([
    { $lookup: { from: target, localField: field, foreignField: '_id', as: 'match' } },
    { $match: { match: { $size: 0 } } }, { $limit: 1 }, { $count: 'missing' },
  ]).toArray()[0]?.missing || 0;
}
for (const [name, expected] of Object.entries(manifest.files)) {
  const path = `/workspace/data/${name}.json`;
  const hash = crypto.createHash('sha256').update(fs.readFileSync(path)).digest('hex');
  ensure(hash === expected.sha256, `${name}.json checksum`);
  ensure(db.getCollection(name).countDocuments({}) === expected.count, `${name} count`);
  print(`${name}: ${expected.count} documents; file SHA-256 ${hash}`);
}
for (const [name, count] of Object.entries({
  titles: 500, users: 2000, watch_events: 50000, reviews: 5000, plans: 3,
})) ensure(manifest.files[name]?.count === count, `${name} target count`);
ensure(manifest.files.payments?.count > 0, 'payment records');
for (const [name, target, field] of [
  ['watch_events', 'users', 'userId'], ['watch_events', 'titles', 'titleId'],
  ['reviews', 'users', 'userId'], ['reviews', 'titles', 'titleId'],
  ['payments', 'users', 'userId'], ['payments', 'plans', 'plan'],
  ['users', 'plans', 'subscription.plan'],
]) ensure(!missingReference(name, target, field), `${name}.${field} reference`);
for (const [name, fields] of Object.entries({
  users: { _id: 'objectId', joinedAt: 'date', 'subscription.startedAt': 'date' },
  titles: { _id: 'objectId', releaseYear: 'int' },
  watch_events: { _id: 'objectId', userId: 'objectId', titleId: 'objectId',
    startedAt: 'date', minutesWatched: 'int', completed: 'bool' },
  reviews: { userId: 'objectId', titleId: 'objectId', createdAt: 'date' },
  payments: { userId: 'objectId', paidAt: 'date', periodStart: 'date', periodEnd: 'date' },
})) {
  const invalid = Object.entries(fields).map(([field, type]) => ({
    [field]: { $not: { $type: type } },
  }));
  ensure(db.getCollection(name).countDocuments({ $or: invalid }) === 0, `${name} required BSON types`);
}
ensure(db.titles.countDocuments({ type: 'movie', runtimeMin: { $type: 'int' }, seasons: { $exists: false } }) === 400,
  'movie runtime and shape');
ensure(db.titles.countDocuments({ type: 'series', seasons: { $type: 'array' }, runtimeMin: { $exists: false } }) === 100,
  'series seasons and shape');
ensure(db.users.countDocuments({ email: { $not: /^bingeling-[0-9]{6}@example\.com$/ } }) === 0,
  'only synthetic example.com addresses');
ensure(db.titles.countDocuments({ type: 'movie', genres: 'Thriller', releaseYear: { $gt: 2018 } }) > 0,
  'Q1 recent thriller');
ensure(db.users.countDocuments({ 'subscription.plan': 'premium', 'subscription.status': 'active' }) > 0,
  'Q2 active premium');
ensure(db.titles.countDocuments({ 'cast.name': manifest.demoActor }) > 0,
  'Q5 actor anchor');
const anchor = ObjectId(manifest.demoUserId);
ensure(db.users.countDocuments({ _id: anchor }) === 1 && db.watch_events.countDocuments({ userId: anchor }) > 0,
  'Q4 user anchor');
const binge = db.watch_events.aggregate([
  { $match: { userId: anchor, titleId: ObjectId(manifest.bingeTitleId),
    completed: true, season: { $type: 'int' }, episode: { $type: 'int' } } },
  { $group: { _id: { day: { $dateToString: { format: '%Y-%m-%d', date: '$startedAt',
    timezone: 'Asia/Kolkata' } }, season: '$season' }, episodes: { $addToSet: '$episode' } } },
  { $match: { 'episodes.2': { $exists: true } } }, { $limit: 1 },
]).hasNext();
ensure(binge, 'Q8 binge anchor: three distinct completed episodes on one India day');
const sourceEvents = db.watch_events.countDocuments({ origin: 'movielens-rating-proxy' });
ensure(sourceEvents > 0, 'rating-backed event proxies');
const syntheticEvents = db.watch_events.countDocuments({ origin: /^synthetic/ });
ensure(sourceEvents === manifest.provenance.realRatingProxyEvents, 'real event provenance');
ensure(syntheticEvents === manifest.provenance.syntheticEvents, 'synthetic event provenance');
ensure(sourceEvents + syntheticEvents === manifest.files.watch_events.count, 'every event has provenance');
ensure(sourceEvents / manifest.files.watch_events.count >= 0.9,
  'at least 90% rating-backed event proxies');
ensure(manifest.provenance.realRatingReviews === manifest.files.reviews.count,
  'every review backed by a source rating');
ensure(db.reviews.countDocuments({ origin: 'movielens-rating' }) === manifest.provenance.realRatingReviews,
  'real review provenance');
ensure(db.payments.countDocuments({ origin: 'synthetic' }) === manifest.files.payments.count,
  'payment provenance');
printjson({ valid: true, realRatingProxyEvents: sourceEvents,
  realEventShare: sourceEvents / manifest.files.watch_events.count,
  realRatingReviews: manifest.provenance.realRatingReviews,
  syntheticEvents, demoUserId: manifest.demoUserId, demoActor: manifest.demoActor });
