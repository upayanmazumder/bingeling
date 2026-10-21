// Q5: Find titles that feature a given actor.
// Intent: Match an actual credited actor against the embedded cast array.
// Collections: titles; actor anchor from data/manifest.json.
const demoActor = JSON.parse(require('fs').readFileSync('data/manifest.json', 'utf8')).demoActor;
const filter = { cast: { $elemMatch: { name: demoActor } } };
printjson({ actor: demoActor, totalMatches: db.titles.countDocuments(filter), showingFirst: 10 });
db.titles.find(
  filter,
  { name: 1, type: 1, releaseYear: 1, cast: 1 }
).sort({ name: 1 }).limit(10).forEach(row => printjson(EJSON.stringify(row)));
