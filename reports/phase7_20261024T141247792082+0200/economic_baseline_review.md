# Phase 7 economic baseline review

Status: validated candidate ready for review/approval; NOT promoted.
Run timestamp: 24 October 2026, 14:12:47 Europe/Rome (UTC+02:00).
This report distinguishes calculated facts from economic interpretation.

## Verified controls and evidence

- A byte-verified timestamped backup of all 19 processed CSVs was created before
  generation, retaining original schemas and recording SHA-256/size/row/header
  metadata in its manifest.
- 61 automated tests passed. Three disposable-folder tests initially could not
  complete under sandbox filesystem restrictions; the SAME checks passed with
  required filesystem access before any regeneration. This was not suppressed
  or treated as a validation pass. The controlled runner also recorded 61 passing
  tests in tests.log.
- 19 candidate CSVs were generated in data/staging exclusively; all were read back
  and checked with strict Phase 1-6 schemas plus master, operational, raw-material,
  manufacturing allocation, FG/sales component, freight, opex and P&L validators.
- A complete independent generation and readback validation in data/staging_repro_*
  produced identical SHA-256 hashes for all 19 CSVs. The isolated temporary folder
  was removed after success; both hash sets are retained in reproducibility.json.
- Protected processed/raw/SQL/Power BI file hashes are unchanged. No database was
  accessed, existing reports were not rebuilt, and no candidate promotion occurred.
- Runtime: Python 3.12.14, pandas 3.0.1, numpy 2.3.5; seeds 360/361/362. Source
  hashes are in validation_results.json. Reproducibility is verified within this
  recorded runtime, not claimed across arbitrary dependency versions/platforms.

## Candidate financial results

All money below is EUR; percentages are ratios of summed profits/revenue, not
averages of product margins. Full precision is in financial_comparison.csv.

| Period | Net Revenue | Manufacturing COGS | Gross Profit | Gross Margin % | Outbound Freight | Selling | Administration | Operating Profit | Operating Margin % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2024 | 10,559,374.25 | 8,095,663.36 | 2,463,710.89 | 23.33 | 286,376.98 | 525,761.49 | 459,762.00 | 1,191,810.42 | 11.29 |
| 2025 | 10,973,277.52 | 8,411,512.20 | 2,561,765.32 | 23.35 | 295,196.43 | 539,655.54 | 467,970.00 | 1,258,943.35 | 11.47 |
| combined | 21,532,651.77 | 16,507,175.56 | 5,025,476.21 | 23.34 | 581,573.41 | 1,065,417.03 | 927,732.00 | 2,450,753.77 | 11.38 |

Idle-line and fully defective-batch production expenses are zero in this realized
candidate. Their policies and edge cases remain covered by regression tests.

## Legacy comparison

| Period | Net Revenue | Manufacturing COGS | Gross Profit | Gross Margin % | Outbound Freight | Selling | Administration | Operating Profit | Operating Margin % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2024 | 31,736,590.68 | 11,163,917.74 | 20,572,672.94 | 64.82 | 0.00 | 852,513.83 | 387,168.00 | 19,332,991.11 | 60.92 |
| 2025 | 33,177,878.82 | 11,833,847.78 | 21,344,031.04 | 64.33 | 0.00 | 885,227.59 | 394,080.00 | 20,064,723.45 | 60.48 |
| combined | 64,914,469.50 | 22,997,765.52 | 41,916,703.98 | 64.57 | 0.00 | 1,737,741.42 | 781,248.00 | 39,397,714.56 | 60.69 |

The combined operating margin fell from 60.691730% to 11.381570%, a reduction of
49.310160 percentage points. Gross margin fell from 64.572204% to 23.338864%.
This is NOT explained solely by adding logistics or correcting double-counting:
commercial prices and manufacturing scope were explicitly redesigned in Phases
1-2. Units shipped changed from 366,741 to 361,290 (-1.49%), while weighted net
selling price changed from EUR 177.00 to EUR 59.60 per unit. Production attempts
changed from 379,713 to 376,803 because revised BOMs consume a different number
of seeded random draws in operational generation. IDs/grains remain stable;
old versus new financial changes are not a controlled single-variable experiment.

New production cost consists of EUR 6,815,013.91 purchase materials, 225,753.40
inbound freight, 7,355,229.61 labor, 590,791.68 energy and 1,823,671.43 overhead.
Total capitalized production EUR 16,810,460.03 less ending FG EUR 303,284.47
reconciles to EUR 16,507,175.56 manufacturing COGS. Ending FG is 7,233 units;
ending raw-material stock is 19,035.459 kg valued at EUR 70,296.66. Do not expense
these closing inventory values again. Outbound freight is EUR 581,573.41 and
selling/admin totals EUR 1,993,149.03, both separate from manufacturing COGS.

## Product margin diagnostics and investigated drivers

Product gross margins range from 12.800451% to 34.087976%. No product has a
negative combined gross margin. No sold product/month has a negative gross
margin; the monthly range is 9.738389% (P020, February 2025) to 37.338075%
(P013, July 2024). Relative extremes are reviewed below even though no combined
product breaches the diagnostic CSV's absolute <0% or >35% review thresholds.
Those thresholds are observations only; they never alter assumptions or generation.

| Product | Name | Gross Margin % | Net ASP EUR | Mfg COGS/unit EUR | Contribution after outbound % |
| --- | --- | --- | --- | --- | --- |
| P020 | Transmission Housing 4 | 12.80 | 94.60 | 82.49 | 11.09 |
| P019 | Transmission Housing 3 | 14.36 | 88.22 | 75.55 | 12.60 |
| P018 | Transmission Housing 2 | 16.03 | 82.68 | 69.43 | 14.09 |
| P014 | Suspension Link 2 | 31.97 | 53.56 | 36.44 | 28.97 |
| P005 | Steering Bracket 1 | 32.33 | 38.51 | 26.06 | 28.01 |
| P013 | Suspension Link 1 | 34.09 | 49.59 | 32.69 | 30.87 |

### Lower-margin housing variants: verified facts

P020 has 6.900 kg process input, 0.920 standard person-hours and 13.800 kWh per
attempt. Its sold-unit cost is EUR 36.74 purchase material + 0.85 inbound freight
+ 33.82 labor + 2.86 energy + 8.22 overhead = approximately EUR 82.49 against
EUR 94.60 net selling price. P019 and P018 have similarly high material/processing
intensity and combined gross margins of 14.36%/16.03%. P020's contribution after
outbound freight is 11.09%, before shared selling/admin.

Interpretation: the high input/processing requirements explain the lower margins;
there is no missing freight deduction or duplicated component. Larger variants
scale physical input/activity faster than commercial prices: size factors span
0.85-1.15 while price factors span 0.90-1.11. Month-level rates, defects, product
mix and fixed-pool absorption can further compress margins. Review housing
commercial positioning and routing assumptions with a domain reviewer; no
prices/costs were changed after observing these results.

### Higher-margin small variants: verified facts

P013 has 3.612 kg process input, 0.425 standard person-hours and 5.950 kWh per
attempt. Its sold-unit cost is EUR 11.54 purchase material + 0.43 inbound freight
+ 15.62 labor + 1.26 energy + 3.84 overhead = approximately EUR 32.69, against
EUR 49.59 net selling price. P005 has 2.745 kg, 0.340 hours and 4.250 kWh, with
EUR 26.06 sold-unit manufacturing cost against EUR 38.51 net price. P014 is also
among the higher-margin products (31.97%).

Interpretation: smaller variants have lower physical requirements relative to
their independently assumed prices; activity-based allocation assigns them fewer
conversion costs. Their higher gross margins are traceable rather than imposed.
They are not product operating margins: shared selling/admin is intentionally
not allocated. Product/month detail is provided for further review.

## Economic readiness and limitations

Judgment: this is a substantially more credible internally consistent synthetic
baseline than the 60.69% operating-margin legacy model. An 11.38% operating margin
still needs domain review and is not verified as an industry benchmark. No target
margin was used, no post-generation calibration was performed, and there are no
unresolved arithmetic/reconciliation failures.

Normal-capacity absorption remains simplified: all fixed conversion cost on an
active line is absorbed; only a zero-attempt line expenses its full pool. Effective
unit-capacity utilization ranges from 68.05% to 93.83%; standard person-hours do
not establish machine/staffing feasibility. Rates and BOMs are fictional, freight
is blended, and warranty/R&D/subcontracting coverage, WIP, returns, scrap recovery,
geography/minimum consignment charges and material-specific FG lineage remain
outside this model or require explicit future scope decisions.

Approval recommendation: approve as a staged synthetic candidate for migration
planning and domain review. Do not treat technical validation as authorization
to replace processed data, append facts into PostgreSQL, refresh Power BI or claim
industry-calibrated margins. See migration_readiness.md for integration conditions.
