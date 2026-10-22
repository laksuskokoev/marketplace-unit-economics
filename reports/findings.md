# Business findings — synthetic 90-day window

**Caution:** all data are simulated and all financial assumptions are illustrative; no actual company performance is claimed.

## Business question
Which acquisition channels generate more contribution than their acquisition cost during the first 90 days?

## Definition of metrics
- **GMV**: fulfilled orders' merchandise value; refunds are excluded.
- **Marketplace revenue**: 15% take rate on fulfilled GMV plus 35 RUB delivery fee per fulfilled order.
- **Variable cost**: 2.2% of fulfilled GMV + 65 RUB fulfilment + 12 RUB support per fulfilled order; 45 RUB handling per refunded order.
- **Contribution**: marketplace revenue minus the above variable costs, BEFORE advertising and fixed overhead.
- **CAC**: total channel marketing spend divided by acquired users, including users who never ordered. Organic has an allocated spend; it is not free.
- **90-day contribution per acquired user** (*LTV90 contribution proxy*): aggregated 90-day contribution / all acquired users; this is NOT lifetime LTV.
- **90-day contribution/CAC**: channel 90-day contribution / marketing spend. Greater than 1 means contribution covers budget within observed 90 days, but NOT that business is profitable overall.
- **Net after marketing**: 90-day contribution less acquisition spend, excluding fixed costs, taxes and cost of capital.

## Results

| Channel | CAC, RUB | 90-day contribution/user, RUB | Ratio | Contribution after marketing, RUB |
|---|---:|---:|---:|---:|
| Organic | 100 | 195.9 | 1.96 | 172,612 |
| Referral | 225 | 241.8 | 1.07 | 20,195 |
| Search Ads | 611 | 186.7 | 0.31 | -764,010 |
| Social Ads | 750 | 96.4 | 0.13 | -1,176,561 |

Across all channels: **6,600 acquired users**, **5,046 orders**, total spend **2,900,000 RUB**, contribution before marketing **1,152,236 RUB**, net after marketing **-1,747,764 RUB**.

## Interpretation and suggested decisions
1. **Organic:** highest ratio of 90-day contribution to acquisition spend (≈1.96). Check whether extra organic budget has diminishing returns before scaling.
2. **Referral:** slightly over break-even (≈1.07). Pilot changes to referral incentives with incremental measurement.
3. **Search Ads:** ≈0.31 of 90-day spend is covered by contribution. Review targeting, attribution and cohort mix before further spend.
4. **Social Ads:** ≈0.13 covered. Investigate creative fit, unit economics and refund rate; do not scale based on GMV alone.

**Do not interpret these as causal effects.** Channel users were not randomly assigned. Differences can reflect selection bias. Also 90-day observation cannot establish full lifetime payback. Prices, take rate, costs and channel patterns were generated for education.

## Limitations / next steps
- Marketing spend is illustrative, channel-wide and not attributed to an individual user.
- No taxes, fixed overhead, merchant subsidies, returns after 90 days, seasonality, or future cash flows.
- Every user's acquisition date is from Jan 1 to Mar 6, 2026, and all generated orders fall within 90 days, avoiding right-censoring in this simulation.
- Validate gross margin assumptions with a real finance team; segment by acquisition cohort, device, geography, product category, and run incremental experiments where possible.
