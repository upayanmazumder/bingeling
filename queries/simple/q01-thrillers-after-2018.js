// Q1: List all Thriller movies released after 2018, newest first.
// Intent: Filter the catalogue by type, genre and release year.
// Collections: titles.
const filter = { type: 'movie', genres: 'Thriller', releaseYear: { $gt: 2018 } };
printjson({ totalMatches: db.titles.countDocuments(filter), showingNewest: 10 });
db.titles.find(
  filter,
  { name: 1, releaseYear: 1, genres: 1, language: 1 }
).sort({ releaseYear: -1, name: 1 }).limit(10).forEach(row => printjson(EJSON.stringify(row)));
