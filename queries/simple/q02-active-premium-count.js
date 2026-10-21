// Q2: How many users have an active premium subscription?
// Intent: Count users whose subscription is both premium and active.
// Collections: users.
printjson({ activePremiumUsers: db.users.countDocuments({
  'subscription.plan': 'premium',
  'subscription.status': 'active'
}) });
