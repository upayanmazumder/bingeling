// Q11 (extra): How much work does the index save for the "recent watches" lookup in Q4?
// Intent: Run the Q4 filter and sort twice. Force a collection scan, then force the index.
// Compare the plan stage and the documents examined from explain("executionStats").
// Collections: watch_events; anchor from data/manifest.json.
const demoUserId = ObjectId(
  JSON.parse(require('fs').readFileSync('data/manifest.json', 'utf8')).demoUserId
);
function plan(label, hint) {
  const stats = db.watch_events
    .find({ userId: demoUserId })
    .sort({ startedAt: -1 })
    .limit(10)
    .hint(hint)
    .explain('executionStats');
  const stages = [];
  for (let s = stats.queryPlanner.winningPlan; s; s = s.inputStage) stages.push(s.stage);
  return {
    plan: label,
    stages: stages.join(' > '),
    docsExamined: stats.executionStats.totalDocsExamined,
    keysExamined: stats.executionStats.totalKeysExamined,
    returned: stats.executionStats.nReturned
  };
}
printjson(plan('collection scan', { $natural: 1 }));
printjson(plan('index { userId: 1, startedAt: -1 }', { userId: 1, startedAt: -1 }));
