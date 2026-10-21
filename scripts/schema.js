// Bingeling collection constraints and indexes. Run after mongoimport on bingeling.
const schemas = {
  users: {
    required: ['_id', 'name', 'email', 'country', 'timezone', 'joinedAt', 'subscription'],
    properties: {
      _id: { bsonType: 'objectId' }, name: { bsonType: 'string' },
      email: { bsonType: 'string' }, country: { bsonType: 'string' },
      timezone: { bsonType: 'string' }, joinedAt: { bsonType: 'date' },
      subscription: {
        bsonType: 'object',
        required: ['plan', 'status', 'startedAt', 'endedAt'],
        properties: {
          plan: { enum: ['basic', 'standard', 'premium'] },
          status: { enum: ['active', 'cancelled'] },
          startedAt: { bsonType: 'date' },
          endedAt: { bsonType: ['date', 'null'] },
        },
      },
    },
  },
  titles: {
    required: ['_id', 'type', 'name', 'releaseYear', 'language', 'genres', 'cast'],
    properties: {
      _id: { bsonType: 'objectId' }, type: { enum: ['movie', 'series'] },
      name: { bsonType: 'string' }, releaseYear: { bsonType: 'int' },
      language: { bsonType: 'string' }, genres: { bsonType: 'array' },
      cast: { bsonType: 'array' }, runtimeMin: { bsonType: 'int' },
      seasons: { bsonType: 'array' },
    },
  },
  watch_events: {
    required: ['_id', 'userId', 'titleId', 'titleName', 'device', 'startedAt', 'minutesWatched', 'completed', 'origin'],
    properties: {
      _id: { bsonType: 'objectId' }, userId: { bsonType: 'objectId' },
      titleId: { bsonType: 'objectId' }, titleName: { bsonType: 'string' },
      device: { enum: ['tv', 'mobile', 'web', 'tablet'] },
      startedAt: { bsonType: 'date' }, minutesWatched: { bsonType: 'int', minimum: 1 },
      completed: { bsonType: 'bool' }, origin: { bsonType: 'string' },
      season: { bsonType: 'int' }, episode: { bsonType: 'int' },
    },
  },
  reviews: {
    required: ['_id', 'userId', 'titleId', 'rating', 'text', 'createdAt'],
    properties: {
      _id: { bsonType: 'objectId' }, userId: { bsonType: 'objectId' },
      titleId: { bsonType: 'objectId' }, rating: { bsonType: ['int', 'double'], minimum: 0.5, maximum: 5 },
      text: { bsonType: 'string' }, createdAt: { bsonType: 'date' },
    },
  },
  plans: {
    required: ['_id', 'name', 'priceInr'],
    properties: { _id: { bsonType: 'string' }, name: { bsonType: 'string' },
      priceInr: { bsonType: 'int', minimum: 0 } },
  },
  payments: {
    required: ['_id', 'userId', 'plan', 'amountInr', 'paidAt', 'periodStart', 'periodEnd'],
    properties: {
      _id: { bsonType: 'objectId' }, userId: { bsonType: 'objectId' },
      plan: { enum: ['basic', 'standard', 'premium'] },
      amountInr: { bsonType: 'int', minimum: 0 }, paidAt: { bsonType: 'date' },
      periodStart: { bsonType: 'date' }, periodEnd: { bsonType: 'date' },
    },
  },
};
for (const [collection, schema] of Object.entries(schemas)) {
  const result = db.runCommand({ collMod: collection,
    validator: { $jsonSchema: { bsonType: 'object', ...schema } },
    validationLevel: 'strict', validationAction: 'error' });
  if (result.ok !== 1) throw new Error(`Cannot install ${collection} validator: ${tojson(result)}`);
}
db.users.createIndex({ email: 1 }, { unique: true });
db.titles.createIndex({ genres: 1, releaseYear: -1 });
db.titles.createIndex({ name: 'text', 'cast.name': 'text' }, { language_override: 'textLanguage', default_language: 'none' });
db.watch_events.createIndex({ userId: 1, startedAt: -1 });
db.watch_events.createIndex({ titleId: 1 });
db.watch_events.createIndex({ userId: 1, titleId: 1, startedAt: 1 });
db.reviews.createIndex({ titleId: 1, userId: 1 }, { unique: true });
db.payments.createIndex({ plan: 1, periodStart: 1 });
db.payments.createIndex({ userId: 1, periodStart: 1 }, { unique: true });
print('Schema validators and indexes installed.');
