# Scenario financial reconciliation — reference calculator results

These are independent Python Decimal results from the approved PostgreSQL historical data. They are **not Power BI DAX results**. All eight required cases were evaluated for 2024, 2025 and combined; fourteen boundary/combination cases were additionally evaluated for each period. Full-precision values are in scenario_results_full_precision.json and scenario_results.csv in this report directory.

## All-zero reconciliation

All 33 approved annual/combined comparisons passed, with exact EUR source totals and percentage tolerance 0.00000001 percentage points. Combined revenue remains EUR 21,532,651.77, manufacturing COGS EUR 16,507,175.56, GP EUR 5,025,476.21 and OP EUR 2,450,753.77. Combined operating expenses are EUR 1,993,149.03 (selling plus administration); outbound EUR 581,573.41 is separate. Idle/abnormal expenses are zero in the source candidate. No assumption or source amount was changed.

## Derived direct/support labor exposure

The approved labor COGS total EUR 7,219,604.41 is decomposed analytically into direct EUR 6,889,576.65 and support EUR 330,027.76. Both parts sum exactly to each original sales-row amount. Direct attribution is reconstructed under the documented cent-level monthly weighted-average convention, not claimed to be an originally stored sales field. All 480 monthly ledgers and 2,596 sales-line splits agree between independent Python and SQL implementations.

The old Phase 9A blended-labor +10% formula would also change support COGS by EUR 33,002.7760. Phase 9B removes that unintended support exposure. It does not change baseline total labor or add a sixth booked cost component.

## 2024 — required scenarios

| Scenario | Revenue EUR | COGS EUR | GP EUR | GM % | SG&A EUR | OP EUR | OM % | OP change EUR | OP change % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All zero | 10,559,374.25 | 8,095,663.36 | 2,463,710.89 | 23.33 | 985,523.49 | 1,191,810.42 | 11.29 | 0.00 | 0.00 |
| Materials +10% | 10,559,374.25 | 8,424,398.47 | 2,134,975.78 | 20.22 | 985,523.49 | 863,075.31 | 8.17 | -328,735.11 | -27.58 |
| Direct labor +10% | 10,559,374.25 | 8,432,417.94 | 2,126,956.32 | 20.14 | 985,523.49 | 855,055.85 | 8.10 | -336,754.58 | -28.26 |
| Energy +10% | 10,559,374.25 | 8,124,121.26 | 2,435,252.99 | 23.06 | 985,523.49 | 1,163,352.52 | 11.02 | -28,457.90 | -2.39 |
| Inbound freight +10% | 10,559,374.25 | 8,106,525.90 | 2,452,848.35 | 23.23 | 985,523.49 | 1,180,947.88 | 11.18 | -10,862.54 | -0.91 |
| Outbound freight +10% | 10,559,374.25 | 8,095,663.36 | 2,463,710.89 | 23.33 | 985,523.49 | 1,163,172.72 | 11.02 | -28,637.70 | -2.40 |
| Selling prices +5% | 11,087,342.96 | 8,095,663.36 | 2,991,679.60 | 26.98 | 996,082.86 | 1,709,219.76 | 15.42 | 517,409.34 | 43.41 |
| Materials +10%, prices +5% | 11,087,342.96 | 8,424,398.47 | 2,662,944.49 | 24.02 | 996,082.86 | 1,380,484.65 | 12.45 | 188,674.23 | 15.83 |

## 2025 — required scenarios

| Scenario | Revenue EUR | COGS EUR | GP EUR | GM % | SG&A EUR | OP EUR | OM % | OP change EUR | OP change % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All zero | 10,973,277.52 | 8,411,512.20 | 2,561,765.32 | 23.35 | 1,007,625.54 | 1,258,943.35 | 11.47 | 0.00 | 0.00 |
| Materials +10% | 10,973,277.52 | 8,752,679.19 | 2,220,598.33 | 20.24 | 1,007,625.54 | 917,776.36 | 8.36 | -341,166.99 | -27.10 |
| Direct labor +10% | 10,973,277.52 | 8,763,715.29 | 2,209,562.23 | 20.14 | 1,007,625.54 | 906,740.26 | 8.26 | -352,203.09 | -27.98 |
| Energy +10% | 10,973,277.52 | 8,440,993.34 | 2,532,284.18 | 23.08 | 1,007,625.54 | 1,229,462.21 | 11.20 | -29,481.14 | -2.34 |
| Inbound freight +10% | 10,973,277.52 | 8,422,806.60 | 2,550,470.92 | 23.24 | 1,007,625.54 | 1,247,648.95 | 11.37 | -11,294.40 | -0.90 |
| Outbound freight +10% | 10,973,277.52 | 8,411,512.20 | 2,561,765.32 | 23.35 | 1,007,625.54 | 1,229,423.71 | 11.20 | -29,519.64 | -2.34 |
| Selling prices +5% | 11,521,941.40 | 8,411,512.20 | 3,110,429.20 | 27.00 | 1,018,598.82 | 1,796,633.95 | 15.59 | 537,690.60 | 42.71 |
| Materials +10%, prices +5% | 11,521,941.40 | 8,752,679.19 | 2,769,262.20 | 24.03 | 1,018,598.82 | 1,455,466.96 | 12.63 | 196,523.61 | 15.61 |

## combined — required scenarios

| Scenario | Revenue EUR | COGS EUR | GP EUR | GM % | SG&A EUR | OP EUR | OM % | OP change EUR | OP change % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All zero | 21,532,651.77 | 16,507,175.56 | 5,025,476.21 | 23.34 | 1,993,149.03 | 2,450,753.77 | 11.38 | 0.00 | 0.00 |
| Materials +10% | 21,532,651.77 | 17,177,077.66 | 4,355,574.11 | 20.23 | 1,993,149.03 | 1,780,851.67 | 8.27 | -669,902.10 | -27.33 |
| Direct labor +10% | 21,532,651.77 | 17,196,133.23 | 4,336,518.55 | 20.14 | 1,993,149.03 | 1,761,796.11 | 8.18 | -688,957.67 | -28.11 |
| Energy +10% | 21,532,651.77 | 16,565,114.60 | 4,967,537.17 | 23.07 | 1,993,149.03 | 2,392,814.73 | 11.11 | -57,939.04 | -2.36 |
| Inbound freight +10% | 21,532,651.77 | 16,529,332.50 | 5,003,319.27 | 23.24 | 1,993,149.03 | 2,428,596.83 | 11.28 | -22,156.94 | -0.90 |
| Outbound freight +10% | 21,532,651.77 | 16,507,175.56 | 5,025,476.21 | 23.34 | 1,993,149.03 | 2,392,596.43 | 11.11 | -58,157.34 | -2.37 |
| Selling prices +5% | 22,609,284.36 | 16,507,175.56 | 6,102,108.80 | 26.99 | 2,014,681.68 | 3,505,853.71 | 15.51 | 1,055,099.94 | 43.05 |
| Materials +10%, prices +5% | 22,609,284.36 | 17,177,077.66 | 5,432,206.69 | 24.03 | 2,014,681.68 | 2,835,951.60 | 12.54 | 385,197.83 | 15.72 |

## What each result proves

- Material, inbound, energy and direct-labor cost changes affect their recognized COGS exposure; other COGS components and fixed SG&A remain unchanged. Support labor is fixed in the direct-labor case.
- Outbound +10% leaves GP and GM unchanged and lowers OP by 10% of base distribution expense.
- Price +5% increases net revenue at fixed quantities and also increases variable selling. OP improvement is price_change × (base revenue − base variable selling), not the full revenue increase.
- The combined material/price OP change equals the sum of isolated changes under this linear static model.
- All six zero inputs reproduce the approved ledger-derived P&L; no financial target is backsolved.

## Validation totals

| Reference check | Passed |
|---|---:|
| Required scenario-period cases | 24 |
| Additional boundary/combined cases | 42 |
| Total scenario-period cases | 66 |
| Independent closed-form GP/OP delta comparisons | 132 |
| COGS and P&L conservation checks | 66 each |
| Zero-baseline monetary/percentage comparisons | 33 |
| Existing SQL integrity checks | 36 |
| Existing SQL financial comparisons | 33 |
| Direct/support monthly ledgers | 480 |
| SQL/Python sale-line exposure matches | 2,596 |
| In-memory mathematical edge tests | 15 |

All 66 outcomes preserve fixed support labor, overhead, fixed selling and administration. Parameters are bounded −50% to +100%; the range is illustrative sensitivity, not a forecast confidence interval.

## Rounding and acceptance

Reference calculations retain fractional cents; table entries are independently rounded half-up only for display. A displayed OP minus displayed baseline can differ by one cent from an independently displayed delta at an exact half-cent tie. Preserve the full-precision result as reference and investigate DAX numeric type/presentation differences; never silently alter source accounting to force a displayed equality. DAX percentages are fractions and the Desktop matrix multiplies them by 100 for comparison to these report percentages.

Actual DAX compilation, M execution, parameter slicers and visuals remain pending inside Desktop. Static code checks and this independent calculator cannot certify those runtime behaviors.
