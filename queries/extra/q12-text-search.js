// Q12 (extra): Which titles match a text search on title and cast names?
// Intent: Use the text index on name and cast.name. Rank matches by text score.
// Collections: titles; search term is the demo actor from data/manifest.json.
const term = JSON.parse(require('fs').readFileSync('data/manifest.json', 'utf8')).demoActor;
printjson({
  searchTerm: term,
  matches: db.titles.countDocuments({ $text: { $search: `"${term}"` } }),
  showingTop: 10
});
db.titles
  .find(
    { $text: { $search: `"${term}"` } },
    { _id: 0, name: 1, type: 1, releaseYear: 1, score: { $meta: 'textScore' } }
  )
  .sort({ score: { $meta: 'textScore' }, name: 1 })
  .limit(10)
  .forEach((row) => printjson(EJSON.stringify(row)));
