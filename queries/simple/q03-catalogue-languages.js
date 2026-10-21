// Q3: Which languages are in the catalogue?
// Intent: List unique title languages alphabetically.
// Collections: titles.
printjson(db.titles.distinct('language').sort());
