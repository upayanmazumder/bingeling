// Q9: What is the monthly revenue and churn per plan?
// Intent: Sum actual payments by UTC payment month; churn is cancellations in that month
// divided by subscribers active at its start (null when that denominator is zero).
// Collections: payments, plans, users. Months shown have at least one payment.
const monthly = db.payments
  .aggregate([
    {
      $group: {
        _id: {
          plan: '$plan',
          month: { $dateTrunc: { date: '$paidAt', unit: 'month', timezone: 'UTC' } }
        },
        revenueInr: { $sum: '$amountInr' },
        payments: { $sum: 1 }
      }
    },
    { $lookup: { from: 'plans', localField: '_id.plan', foreignField: 'name', as: 'planDetails' } },
    { $unwind: '$planDetails' },
    { $set: { nextMonth: { $dateAdd: { startDate: '$_id.month', unit: 'month', amount: 1 } } } },
    {
      $lookup: {
        from: 'users',
        let: { plan: '$_id.plan', month: '$_id.month', nextMonth: '$nextMonth' },
        pipeline: [
          { $match: { $expr: { $eq: ['$subscription.plan', '$$plan'] } } },
          {
            $facet: {
              activeAtMonthStart: [
                {
                  $match: {
                    $expr: {
                      $and: [
                        { $lte: ['$subscription.startedAt', '$$month'] },
                        {
                          $or: [
                            { $eq: ['$subscription.endedAt', null] },
                            { $gt: ['$subscription.endedAt', '$$month'] }
                          ]
                        }
                      ]
                    }
                  }
                },
                { $count: 'count' }
              ],
              cancelledDuringMonth: [
                {
                  $match: {
                    $expr: {
                      $and: [
                        { $eq: ['$subscription.status', 'cancelled'] },
                        { $gte: ['$subscription.endedAt', '$$month'] },
                        { $lt: ['$subscription.endedAt', '$$nextMonth'] }
                      ]
                    }
                  }
                },
                { $count: 'count' }
              ]
            }
          }
        ],
        as: 'subscriberStats'
      }
    },
    {
      $set: {
        activeAtMonthStart: {
          $ifNull: [{ $first: { $first: '$subscriberStats.activeAtMonthStart' } }, null]
        },
        cancelledDuringMonth: {
          $ifNull: [{ $first: { $first: '$subscriberStats.cancelledDuringMonth' } }, null]
        }
      }
    },
    {
      $set: {
        activeAtMonthStart: { $ifNull: ['$activeAtMonthStart.count', 0] },
        cancelledDuringMonth: { $ifNull: ['$cancelledDuringMonth.count', 0] }
      }
    },
    {
      $project: {
        _id: 0,
        month: '$_id.month',
        plan: '$_id.plan',
        planPriceInr: '$planDetails.priceInr',
        payments: 1,
        revenueInr: 1,
        activeAtMonthStart: 1,
        cancelledDuringMonth: 1,
        churnRatePct: {
          $cond: [
            { $gt: ['$activeAtMonthStart', 0] },
            {
              $round: [
                { $multiply: [{ $divide: ['$cancelledDuringMonth', '$activeAtMonthStart'] }, 100] },
                2
              ]
            },
            null
          ]
        }
      }
    },
    { $sort: { month: 1, plan: 1 } }
  ])
  .toArray();
printjson({ totalPlanMonths: monthly.length, showingFirst: Math.min(20, monthly.length) });
monthly.slice(0, 20).forEach((row) => printjson(EJSON.stringify(row)));
