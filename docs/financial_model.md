# Financial model: accounting contract and engineering assumptions

## Status and provenance

Implementation scope: financial improvement plan Phases 1-7. Phase 7 produced a
validated, unpromoted candidate in data/staging; existing processed CSVs remain
the untouched legacy baseline. See staging_workflow.md and the run reports.
Assumption version: `engineering-v1`, owned by `scripts/economic_assumptions.py`.
All new values are fictional design assumptions, not verified market quotes,
engineering specifications, wage surveys or a claim of validated profitability.
They are explicit and independently reviewable. No target profit margin is an
input. Prices and expenses must never be backsolved from realized costs/profit.
Existing processed CSVs have NOT been migrated or regenerated.

The generator headers' historical labels "Phase 1 operations" and "Phase 2
financials" describe the original project, not the new improvement-plan phases.

## Manufacturing scope

The business is a small three-line supplier machining, forming, joining and
assembling metal/rubber/polymer subassemblies. Products are intermediate parts,
not complete safety-certified vehicle systems. "Brake Assembly" means a simple
carrier/bracket subassembly, not a complete hydraulic brake or friction system.
Transmission housings are machined from purchased near-net aluminium inputs;
there is no in-house primary smelting/foundry. BOM kg are gross process inputs
per attempted unit, with separately recorded extra process waste. Routine
finishing/inspection is in labor hours. Materials are a simplified homogeneous
valuation of constituent inputs, including simple moulded inserts; this model
does not claim a detailed purchased-component or subcontracting BOM.

Each line is a flexible cell, potentially staffed by several operators. Labor
hours are aggregate person-hours, not machine cycle time. Existing unit-based
capacity is retained; it is not proof of labor/machine capacity feasibility.
Phase 4 adds external inbound consolidated truck transport. Internal handling
remains in existing plant resources. Phase 6 separately expenses external
outbound delivery when product units ship.

## Accounting policies and cost classification

- EUR only, one warehouse, January 2024 through December 2025, monthly periodic
  accounting. Receipts precede consumption and completions precede month-end
  shipments. Do not infer daily availability from receipt/shipment dates.
- Raw materials: opening stock at reference purchase cost plus estimated inbound
  freight at the base rate. External inbound freight is capitalized separately
  from purchase-material value. Both components use monthly periodic weighted
  average including opening stock. Purchases and freight are not also P&L
  expenses when landed consumption enters manufacturing cost and later COGS.
- Manufacturing: material issues plus labor, energy and manufacturing overhead.
  Hours and kWh use product drivers plus fixed line activity. The labor pool
  includes direct production and support labor; do not label the whole pool
  direct labor. Hourly rates include employer contributions and benefits.
- Conversion allocation uses standard production hours for production labor,
  support labor and overhead; standard activity kWh for activity/standby energy.
  Fixed pools fall back to attempted units only when their primary activity sum
  is zero. With no attempts, fixed costs are expensed as idle costs.
- Defects and extra waste: inputs are consumed for attempted units, including
  defects. Costs are absorbed into good output. Zero-good-output batches expense
  all assigned cost. No scrap revenue, returns, rework ledger or WIP is modeled.
- Idle costs: a line with zero attempts expenses all conversion costs. Otherwise
  unused-capacity costs are absorbed. This is a synthetic simplification, not a
  claim of compliance with normal-capacity inventory accounting.
- Manufacturing overhead excludes labor, energy, material and freight. Base
  line/month coverage is maintenance/consumables 8-10k, occupancy 4-6k and plant
  depreciation 10-12k EUR. The current generator samples the aggregate 22-28k;
  those explanatory components are not separately randomized/booked.
- Finished goods: zero initial balance, monthly weighted-average value for each
  of purchase materials, inbound freight, labor, energy and overhead. Unsold
  component costs carry forward; only shipments become component COGS. Aggregate
  values are sums of authoritative booked components, not independently rounded.
- Selling expense in operating_expenses excludes outbound freight and shop-floor
  costs. Freight is a separate selling/distribution line sourced from sales.
  Administration excludes plant overhead. Shared expenses are company-level;
  do not allocate them to product operating profit silently.
- Gross profit = net revenue - manufacturing sales COGS. Operating profit =
  gross profit - outbound freight - selling - administration - idle conversion
  expense - zero-good-output production-loss expense.
  Interest and income tax are outside scope; operating profit is not net profit.
- Inbound and outbound freight are implemented in source with distinct owners.
  Inbound freight enters inventory and manufacturing COGS; outbound freight is a
  shipment-time selling/distribution expense sourced only from sales. Existing
  CSVs retain the old baseline. Never expense inbound freight again through
  overhead/opex or put outbound freight into manufacturing inventory/COGS.

## Explicit economic assumptions

Family inputs before size variants:

| Family | Base list EUR | Labor person-hours/attempt | kWh/attempt | Process-input BOM kg/attempt |
|---|---:|---:|---:|---|
| Brake Assembly | 65 | 0.55 | 8 | Steel 4; cast iron 3; polymer 0.2; rubber 0.15 |
| Steering Bracket | 44 | 0.40 | 5 | Steel 2.8; stainless steel 0.35; polymer 0.08 |
| Engine Mount | 52 | 0.45 | 6 | Steel 3.2; aluminium 0.7; rubber 0.6 |
| Suspension Link | 57 | 0.50 | 7 | Steel 3.8; rubber 0.25; stainless steel 0.2 |
| Transmission Housing | 88 | 0.80 | 12 | Aluminium 5.5; steel 0.4; polymer 0.1 |

Four size/complexity variants multiply BOM, hours and kWh by 0.85, 0.95, 1.05,
1.15. Independent commercial price multipliers are 0.90, 0.97, 1.04, 1.11.
These price points represent assumed negotiated subassembly positioning, not
cost-plus pricing. Existing customer discounts and +/-2% transaction variation
remain. Price and labor/overhead/fixed-opex escalation is linear 0.15% per month,
not compounded. Purchase inflation remains 0.2% per month with existing supplier
and price variation. Existing material reference EUR/kg values are unchanged.
Unused material catalog IDs remain valid and keep approved suppliers.

| Line | Monthly support person-hours | Monthly base kWh |
|---|---:|---:|
| L01 | 120 | 2400 |
| L02 | 135 | 2800 |
| L03 | 150 | 3200 |

Support covers line coordination, setup support and routine quality oversight.
Base energy covers cell standby and shared services, excluding energy already
included in product kWh. Fixed activity persists with zero attempts.

Fully burdened shop-floor hourly rates are sampled at EUR 32-36 before monthly
escalation; tariffs remain EUR 0.16-0.23/kWh. No separate payroll burden is added.
Selling fixed base is EUR 26k/month: four staff at roughly 5k/month burdened plus
6k office/customer support. Administration is EUR 38k/month: six staff at roughly
5k plus 8k IT/professional services. Variable selling cost is 2% of net revenue
for commissions/commercial support. It is not freight or a profit-balancing item.
Staff counts are explanatory resource assumptions, not new employee facts.

Economic effect: family BOMs replace arbitrary material combinations; product
activity changes line cost with mix; lower, explicit commercial price points
replace random EUR 90-280 prices; overhead and opex cover defined resources.
Loss-making products/months are allowed. Realized profitability is unverified
until a later authorized complete regeneration and review; no margin is promised.

## Added schema and calculation ownership

All existing CSV names, business-key formats and product-to-line assignments are
retained. Existing columns remain. New fields are appended on future export.

| CSV | New fields | Owner |
|---|---|---|
| products | standard_labor_hours_per_attempt; standard_energy_kwh_per_attempt | 02 |
| production_lines | support_labor_hours_per_month; base_energy_kwh_per_month | 02 |
| manufacturing_costs | production_labor_hours; support_labor_hours; activity_energy_kwh; base_energy_kwh | 04 |
| operating_expenses | fixed_amount_eur; variable_rate_pct; variable_driver_amount_eur | 04 |
| manufacturing_costs (Phase 3) | production_labor_cost_eur; support_labor_cost_eur; activity_energy_cost_eur; standby_energy_cost_eur; idle_labor_cost_eur; idle_energy_cost_eur; idle_overhead_cost_eur | 04 |
| production_cost_allocation (Phase 3) | production_labor_cost_eur; support_labor_cost_eur; activity_energy_cost_eur; standby_energy_cost_eur | 04 |

`variable_rate_pct` stores percentage points: 2.0 means 2%, not 200%.

```text
Production labor hours = sum(attempted units * product standard hours)
Labor hours = production labor hours + line support hours
Activity kWh = sum(attempted units * product standard kWh)
Energy kWh = activity kWh + line base kWh
Labor cost = labor hours * burdened hourly rate
Energy cost = energy kWh * tariff
Opex = fixed amount + variable driver amount * variable rate pct / 100
```

Activity totals are rounded to two decimals before valuation. Monetary totals
use integer cents. Fixed and variable opex portions are rounded separately;
`amount_eur` is their sum. Largest-remainder cent allocation is retained,
with conversion weights now supporting exact decimal activity rather than
truncating fractional hours/kWh. Integer-weight sales COGS splits are unchanged.
Phase 4 replaces the old last-row raw-material residual rule with separate
largest-remainder purchase/freight splits using stable production ID ties. Displayed unit rates/costs are informational, not authoritative balances.
`economic_assumptions.py` owns settings/activity arithmetic; 02 builds masters;
03 validates masters and values material flows; 04 owns financial costs/P&L.

## Dataset grains and relationships

| Dataset | Unique grain/key | Relationships/role |
|---|---|---|
| products | product_id | category and line_id; product dimension |
| materials | material_id | kg unit and reference cost |
| suppliers | supplier_id | supplier dimension |
| customers | customer_id | customer segment |
| production_lines | line_id | line dimension and fixed activity |
| material_suppliers | material_id, supplier_id | approved-source bridge |
| bom | product_id, material_id | current recipe; no effective-date history |
| months | month_id | month-start date key |
| line_month_capacity | month_id, line_id | nominal/effective unit capacity |
| production | production_id; also month_id, product_id | attempted/defective/good output |
| material_consumption | production_id, material_id | issues; month/product via production |
| purchase_order_lines | po_line_id | material/supplier and order/expected dates |
| material_receipts | receipt_id | po_line_id; current generator fully receives each PO once |
| raw_material_inventory | month_id, material_id | monthly quantity/value snapshot |
| manufacturing_costs | month_id, line_id | conversion cost pools |
| production_cost_allocation | production_id | assigned material/conversion cost |
| finished_goods_inventory | month_id, product_id | monthly quantity/value snapshot |
| sales | sales_line_id | month/product/customer; fulfilled requests only |
| operating_expenses | month_id, expense_category | company-level selling/admin |

Use dimensions to filter separate facts. Never join sales lines directly to BOM
or issues without aggregating to a common grain. Avoid ambiguous product/line
filter paths. Inventory snapshots are not additive across months. Rate/unit-cost
columns must not be summed; margin = total profit / total net revenue. Completely
unfulfilled requests are missing from sales; use FG demand/unfulfilled totals.

## Reconciliation contract

1. Keys unique, FKs valid, numeric values finite/nonnegative; positive master
   prices, physical requirements and activity drivers. Quantities integral where
   they represent units. Stable business IDs; no row-position joins.
2. PO quantities/prices match receipts under the current full-receipt policy.
3. Raw stock: opening + receipts - consumption = closing in kg. In EUR use
   opening + landed receipts - landed issues = closing, also independently for
   purchase-material and freight. Purchase-only receipt_value_eur must NOT be
   used as the total inventory addition. Each closing component carries forward.
4. Required kg = attempted units * BOM kg, rounded to three decimals. Consumed
   kg = required kg + extra waste. Good = attempted - defective.
5. Driver totals agree with product quantities and fixed line activity. Conversion
   pools equal assigned cost plus idle expense, with deterministic cent residuals.
6. Manufacturing cost = purchase material + inbound freight + labor + energy +
   overhead = capitalized production + zero-good-output expense, also by component.
   Existing material_cost_eur is the landed aggregate; never add it to its parts.
7. FG: opening + production - shipments = closing units; for every component,
   opening value + capitalized production - COGS = closing value. Carry each
   closing component into the next opening, starting at zero.
8. Sales shipments/COGS equal FG totals, for each component and in aggregate;
   sales-row COGS equals its five components. Gross revenue - discounts = net revenue.
9. Fixed plus explicit variable opex equals amount_eur. Outbound freight equals
   actual shipped units times the booked rate and is recognized once, from sales.
   Company P&L includes that expense separately and reconciles to monthly totals.
   Do not deduct purchases, material issues, conversion pools or production costs
   again after recognizing sales COGS. Do not add totals to their components.

Profitability diagnostics are review observations, not pass/fail targets that
rewrite data. Review outlier product costs, margins, resource hours and BOM mass.

## Migration and compatibility

No CSV or database migration occurs in these phases. Current files retain the
old assumptions and lack new drivers. Revised financial cost generation rejects
missing driver columns explicitly, without silently falling back or overwriting
files. Original operational validation still accepts legacy masters for audits.
Importing 02 no longer writes files; `build_masters()` is pure and `main()` alone
exports. Seeds remain 360/361/362; revised output will be reproducible, not
byte-identical to the old synthetic draws. Product/material/customer/supplier/line
ID formats and product assignments remain; BOM relationships deliberately change.

Before future regeneration: approve backup/staging and coordinated master ->
operations -> financial rebuild. Do not regenerate only masters or reuse old
material issues with new BOMs. Update PostgreSQL imports to explicit columns and
use numeric money/rates. Existing SQL production analysis uses unchanged fields.
New fields do not require new relationships, but positional COPY/SELECT * and
Power Query column-count assumptions need review. No database/PBIX is changed.
The previous archive review did not fully inspect binary DAX/relationships; audit
those before model integration. Changing source alone does not update dashboards.

## Phase 3 activity-based conversion allocation

Engineering assumption version remains `engineering-v1`; no prices, wage rates,
BOMs, overhead amounts or operating-expense assumptions changed in Phase 3.
The methodology below supersedes the old attempted-unit allocation.

For product production record i within a line/month:

```text
H_i = attempted_units_i * standard_labor_hours_per_attempt_i
E_i = attempted_units_i * standard_energy_kwh_per_attempt_i
```

Use exact decimal activity weights, before rounding line totals. This retains
small activities and prevents truncation of weights below one hour or kWh.
Line activity totals are still rounded to two decimals, as in Phases 1-2, for
valuation. Do not recompute booked cost by multiplying rounded product shares.

### Pool valuation and allocation

Aggregate labor/energy amounts remain authoritative and are unchanged:

```text
L = cents(line labor_hours * hourly_rate_eur)
Production labor pool = cents(line production_labor_hours * hourly_rate_eur)
Support labor pool = L - production labor pool

K = cents(line energy_kwh * energy_tariff_eur)
Activity energy pool = cents(line activity_energy_kwh * energy_tariff_eur)
Standby energy pool = K - activity energy pool
```

Support and standby take residual cents from splitting aggregate values, so the
subpools always sum exactly to their existing aggregate columns. Their rounded
values may differ from a separately rounded support-hours/base-kWh multiplication
by one cent. This residual convention does not change underlying rates.

| Pool | Primary weight | Zero-primary-weight rule |
|---|---|---|
| Production labor | H_i | Expense any unsupported pool as idle labor; no invented activity |
| Support labor | H_i | Attempted units if any; otherwise idle labor |
| Activity energy | E_i | Expense any unsupported pool as idle energy |
| Standby energy | E_i | Attempted units if any; otherwise idle energy |
| Manufacturing overhead | H_i | Attempted units if any; otherwise idle overhead |

Support and overhead follow labor effort as proxies for coordination and cell
resource usage. Standby follows energy activity as a proxy for cell service use.
These are allocation assumptions, not measured causal costs or normal-capacity
absorption. Positive per-product standard drivers remain mandatory in master
validation; missing/zero/negative/nonfinite standards fail rather than silently
fall back. Zero-primary-activity fallbacks are defensive allocator behavior and
cover empty/inactive batches. Fixed drivers/rates remain unchanged.

For every pool, allocate floor(pool cents * weight / total weight), then award
remaining cents by descending fractional remainder. Ties use ascending stable
`production_id`, never incidental row position. Zero-weight products receive
zero cost. Conversion generation sorts line/months and production IDs before
random rate draws and allocation; rearranging input CSV rows does not change
results. Sales COGS retains its previous shipment-order tie convention.

Product aggregate columns remain:

```text
labor_cost_eur = production_labor_cost_eur + support_labor_cost_eur
energy_cost_eur = activity_energy_cost_eur + standby_energy_cost_eur
```

The four new product columns audit manufacturing allocations only. They do NOT
add component-level finished-goods valuation or sales COGS. Do not sum aggregate
and subpool columns together. Line idle component columns are subsets of the
existing idle_cost_eur and must not be subtracted from profit a second time.
No new tables, keys, relationships or fact grains are introduced.

### Defects, idle cost and reconciliation

- A zero-attempt product receives no conversion allocation. An empty line/month
  or all-zero-attempt line expenses support, standby and overhead. Empty product
  allocations retain a defined schema for read-only conversion validation.
- Partial defects do not change H_i/E_i because work was attempted. The assigned
  batch cost is absorbed by its good units under the existing policy.
- A batch with no good output expenses its entire assigned material/conversion
  cost. It still receives its activity share: do not redistribute its costs to
  other products or add that loss to allocations again.
- An inactive line with no product records can be costed and validated at the
  conversion layer. The unchanged full ERP validator still requires complete
  product/month production and FG coverage for normal datasets.

Exact-cent identities, by line/month:

```text
Labor pool = sum(product labor allocations) + idle labor
Energy pool = sum(product energy allocations) + idle energy
Overhead pool = sum(product overhead allocations) + idle overhead
Idle cost = idle labor + idle energy + idle overhead

Material issues + conversion pools =
    capitalized production + production-loss expense + idle conversion expense
```

`validate_conversion_costs` checks source identities, activity totals, individual
subpool shares and pool/idle/loss conservation; `validate` additionally checks
inventory, sales and P&L identities. Largest-remainder precision, different labor
and energy shares, invalid input, subhour activity, row permutation, zero attempts,
empty production, mixed/all-defective output and negative mutation tests are
covered by the non-destructive unittest suite. A hand-built two-month ledger
checks compatibility with monthly weighted-average inventory carry-forward.

## Phase 4 inbound freight and raw-material component valuation

Implementation version: `inbound-v1`, alongside unchanged `engineering-v1`
commercial, manufacturing and operating-expense assumptions. No margin target
or realized profit feeds prices, freight or valuation. Freight values below are
fictional modeling assumptions, not verified carrier quotations.

### Freight assumptions and initial balance

Base external consolidated-truck transport is EUR 0.12/kg. This represents
regional/domestic bulk deliveries with fuel included. It excludes unloading,
internal handling, storage, insurance, duties, recoverable taxes and outbound
shipping, avoiding overlap with the existing shop-floor/plant cost coverage.
There is no separate minimum charge or fixed shipment fee in this first model.
Very small deliveries are consequently simplified, not claimed to reflect a
real minimum truck invoice. Unused catalog materials can have zero movement.

```text
Receipt freight rate = round(
    0.12 * supplier factor * material/supplier/month factor
         * (1 + 0.0015 * elapsed month index), 4)
```

Supplier factors lie between 0.90 and 1.10; movement factors between 0.95 and
1.05. SHA-256 keys include `inbound-v1`, seed label 361, supplier, and (for the
movement factor) material/month. Approximate rate envelope for 2024-25 is
EUR 0.1026-0.1434/kg before four-decimal rounding. Variation consumes no numpy
RNG draws, preserving the sequence for purchase price/quantity generation.
Elapsed month index follows the sorted generator calendar starting at zero.

Initial raw-material quantity remains 25% of first-month consumption, rounded
to .001 kg. Opening purchase value uses the material reference EUR/kg; opening
freight uses EUR 0.12/kg, each rounded separately to cents. Opening freight is
an explicit estimated legacy balance, not a current-month receipt or expense.
It is not inferred from a future supplier or the first receipt's realized rate.
Subsequent openings carry the previous month's closing components exactly.

### Receipt fields and rounding

| Column | Meaning in revised exports |
|---|---|
| receipt_value_eur | Purchase-only booked value, preserved meaning |
| purchase_unit_cost_eur | Agreed PO EUR/kg, before freight |
| purchase_value_eur | Alias of purchase-only receipt_value_eur |
| inbound_freight_rate_eur_per_kg | Four-decimal transport rate |
| inbound_freight_eur | Booked freight amount |
| landed_receipt_value_eur | Purchase value plus freight |
| landed_unit_cost_eur | Booked landed value / received kg, rounded to 8 decimals |

```text
Purchase value = round_half_up(received kg * purchase EUR/kg, 2)
Freight value = round_half_up(received kg * freight EUR/kg, 2)
Landed receipt value = purchase value + freight value
```

Amounts are independently rounded with commercial half-up rounding, superseding
the old operations generator's binary-float/banker's rounding for these values.
The landed unit rate derives from rounded booked amounts, so it can differ from
purchase unit cost + freight rate for tiny quantities. Its reconciliation error
is at most 0.0000000051 EUR/kg, or quantity * that bound in extended value.
A zero-kg receipt has zero purchase/freight/landed amounts and landed unit cost 0;
normal generation omits zero-quantity PO/receipt records. Quantities must be
finite, nonnegative and exact multiples of .001 kg.

### Raw-material ledger and issue schema

No new CSV tables, keys or grains are introduced. Phase 4 appends fields to:

- `material_receipts.csv`: the five new receipt columns above, excluding existing
  receipt_value_eur and landed_unit_cost_eur.
- `raw_material_inventory.csv`: for each movement `opening`, `receipt`, `issued`,
  `closing`, append `<movement>_purchase_material_value_eur` and
  `<movement>_inbound_freight_value_eur`. Also append landed_receipt_value_eur,
  weighted_average_purchase_unit_cost_eur and
  weighted_average_inbound_freight_unit_cost_eur.
- `material_consumption.csv`: issued_purchase_material_value_eur,
  issued_inbound_freight_eur, weighted_average_purchase_unit_cost_eur and
  weighted_average_inbound_freight_unit_cost_eur.

Existing opening_value_eur, issued_material_value_eur, closing_value_eur and
weighted_average_unit_cost_eur represent TOTAL LANDED values. Inventory
receipt_value_eur remains purchase-only and equals receipt_purchase_material_value_eur;
use landed_receipt_value_eur in the aggregate inventory roll-forward.

For component c (purchase material or inbound freight):

```text
Available quantity = opening kg + received kg
Available value_c = opening value_c + receipt value_c
Weighted-average unit cost_c = available value_c / available quantity
Issued cents_c = round_half_up(available cents_c * consumed kg / available kg)
Closing cents_c = available cents_c - issued cents_c
```

Calculations use integer cents and integer thousandths of kg. Each component's
monthly issue pool is allocated across consumption rows using largest remainder,
with ascending production_id as the tie-breaker. Zero-quantity rows receive no
cents. This replaces the historical residual-to-last-row issue allocation and
prevents small final rows receiving negative rounding residuals.

```text
issued_material_value_eur =
    issued_purchase_material_value_eur + issued_inbound_freight_eur
```

Aggregate inventory balances and issue values are sums of booked components,
never independently rounded aggregates. Component issue rounding can cause a
one-cent difference from separately rounding total WAC * consumed quantity.
Displayed eight-decimal rates are informational; booked component cents are
authoritative. Zero available quantity requires zero value and zero issues;
consumption beyond availability, negative/nonfinite inputs and unsupported
sub-mill quantities are rejected. Full depletion leaves zero component values.

### Financial integration and compatibility

`03_generate_operations.py` owns flow generation and validation;
`material_valuation.py` contains pure receipt/month valuation and cent allocation;
`economic_assumptions.py` owns the freight rate. None writes files on import.
Materials, BOMs, PO terms, selling prices, conversion pools and operating expense
coverage are unchanged. Sorting material, supplier, month and issue keys makes
revised material flow reproducible under row permutation; revised outputs need
not match legacy binary-float rounding or residual placement.

`04_generate_financials.py` retains material_cost_eur as the landed-material
aggregate. Phase 5 adds purchase_material_cost_eur and inbound_freight_cost_eur
from the separate Phase 4 issue columns and uses those parts in its five-component
total. It does not add freight to the landed aggregate again. Never add issued
freight again to manufacturing totals, overhead or operating expenses.

Validation distinguishes fully legacy input from the complete Phase 4 schema.
Legacy datasets remain readable for audits. If any Phase 4 component fields are
present, all required receipt/inventory/issue fields must be present; partial
upgrades are rejected. Financial activity-driver schema requirements remain.
Existing CSVs stay legacy until a separately authorized coordinated regeneration.
PostgreSQL/PBI imports must later use explicit column lists and update receipt
valuation measures from purchase-only additions to landed additions. Review
queries that equate landed unit cost with PO price. No live model was changed.

Tests exercise hand-calculated receipts/WAC/carry, cent ties, component rounding,
zero movements, corrupt/partial schemas and deterministic rates. A 24-record,
one-product/material fixture satisfies existing full production validation.
A freight-only shock confirms purchase terms and conversion/opex do not change,
while manufacturing material cost changes exactly by freight issued. No full
pipeline or file-export entry point is executed by these tests.

## Phase 5 five-component finished-goods and sales costing

Phase 5 changes costing granularity, not prices, demand assumptions, labor or
energy rates, freight rates, overhead coverage or operating-expense formulas.
The economic assumption versions remain `engineering-v1` and `inbound-v1`.
No target margin is used. All source changes remain unapplied to existing CSVs.

### Production components and backward compatibility

The five authoritative production components are:

| Component label | Production column | Sales/FG COGS column |
|---|---|---|
| material (purchase only) | purchase_material_cost_eur | material_cogs_eur |
| inbound_freight | inbound_freight_cost_eur | inbound_freight_cogs_eur |
| labor | labor_cost_eur | labor_cogs_eur |
| energy | energy_cost_eur | energy_cogs_eur |
| overhead | manufacturing_overhead_eur | overhead_cogs_eur |

Both raw-material issue components are summed by production_id. Existing
material_cost_eur retains its landed-material meaning for compatibility:

```text
material_cost_eur = purchase_material_cost_eur + inbound_freight_cost_eur

total_manufacturing_cost_eur = purchase_material_cost_eur
    + inbound_freight_cost_eur + labor_cost_eur + energy_cost_eur
    + manufacturing_overhead_eur
```

Do not add material_cost_eur to purchase_material_cost_eur or inbound_freight_cost_eur.
The existing material_cost_eur + labor + energy + overhead identity still holds.
Labor and energy retain their Phase 3 direct/support and activity/standby splits;
those subpools are audit detail and must not be added to their aggregates.

For each component label c, production allocation appends:

- `capitalized_<c>_cost_eur`
- `<c>_production_loss_expense_eur`

Positive good output capitalizes the full assigned component, including the
cost of partial defects. Zero-good-output batches expense every assigned
component and capitalize zero. Aggregated capitalized_production_cost_eur and
production_loss_expense_eur are the sums of their respective component fields.
Idle conversion expenses remain in manufacturing_costs and are never capitalized.
The same activity allocation and defective-output policy is retained.

For historical purchase-only inputs with neither Phase 4 issue component,
material issues are interpreted as purchase-only and freight is explicitly zero.
This preserves older fixtures/read-only workflows, not lost freight lineage.
If either issue component is present, both are mandatory and must sum exactly
to issued_material_value_eur. Do not strip Phase 4 fields to migrate a landed
aggregate: its purchase/freight split cannot be reconstructed accurately.

### Finished-goods schema and monthly valuation

At unchanged product/month grain, finished_goods_inventory appends, for each
c in material, inbound_freight, labor, energy, overhead:

```text
opening_<c>_value_eur
production_<c>_value_eur
<c>_cogs_eur
closing_<c>_value_eur
```

Production additions equal the corresponding capitalized production components,
not the full cost of any expensed batch. Opening component balances start at
zero; each later opening carries the previous closing exactly. For component c:

```text
Available units = opening units + good production units
Available cents_c = opening cents_c + capitalized production cents_c
COGS cents_c = round_half_up(available cents_c * shipped units / available units)
Closing cents_c = available cents_c - COGS cents_c
```

Calculations use integer units/cents and exact integer-ratio half-up rounding.
Each component uses the SAME available/shipped quantities. Booked aggregate
opening_value_eur, production_value_eur, cogs_eur and closing_value_eur are sums
of components. weighted_average_unit_cost_eur is the informational combined
available value per unit, rounded to eight decimals.

With five separately rounded components, total COGS can differ from separately
rounding total available value * shipment fraction by up to two cents per
product/month. This is expected. Independently re-rounding that aggregate would
break component conservation. Even a nonzero closing quantity may have zero
booked value after very small component balances round into COGS. Full depletion
always consumes all remaining component cents; no negative residual is allowed.

Zero inventory permits no shipments or capitalized values. Zero shipments leave
all components in stock. A fully defective new batch can coexist with opening
stock shipments: its new cost is expensed, and shipments consume only the opening
inventory component balances. No component cost can be capitalized against zero
good units. Missing/negative/nonfinite components, fractional units, subcent
booked values and over-shipments are rejected.

### Sales allocations and deterministic rounding

sales.csv appends the five COGS columns in the table above. For each product/month
and component, allocate monthly COGS cents proportionally to units_shipped:

```text
Initial row cents = floor(component COGS cents * row units / monthly shipped units)
```

Remaining cents go by descending fractional remainder. Ties use ascending stable
sales_line_id. During generation sales IDs follow deterministic request order;
zero-fulfilled requests are skipped and receive no COGS. Zero-quantity positions
never receive cents. Each row's cogs_eur is the sum of its five component amounts.
An aggregate-only shipment split must NOT replace the sum of component splits.
Empty sales exports retain the complete column schema and numeric types for
validation. No unfulfilled request becomes revenue or COGS.

Product/customer iteration and line/month iteration use canonical keys before
random draws. Reordering inputs or sales rows does not change component results.
Operating-expense month iteration is now chronological so shuffled calendars do
not change the existing escalation calculation; no expense rate/base changed.

### Implementation, validation and migration

`finished_goods_valuation.py` owns pure five-component month valuation and sales
cent allocation. It reuses Phase 4 integer-ratio and largest-remainder utilities.
`04_generate_financials.py` owns source extraction, component capitalization/loss,
financial generation and validation. No module writes files on import.

`validate_finished_goods_components` checks production sources, per-component
capitalization/loss, opening/production/COGS/closing, carry-forward and sales-row
allocation. Aggregate fields are checked against sums of booked component cents.
The full financial validator also retains existing activity, quantity, revenue,
discount, opex and P&L checks. Fully legacy allocation/sales/FG frames retain the
old aggregate validation path; any partial Phase 5 upgrade is rejected. Revised
sales/FG generation requires complete component production allocation.

New schema is additive, without changed keys or grains. Existing totals remain
usable, but formulas relying on aggregate-only rounding must use component sums.
Explicit PostgreSQL COPY and Power Query column mappings must be reviewed before
future imports. Material means purchase-only in material_cogs_eur; the similarly
named production material_cost_eur deliberately remains landed. Do not join sales
to consumption/BOM detail without aggregation to avoid multiplying revenue/COGS.
Existing CSVs/PBIX/SQL/database have not been migrated or updated.

Tests include independent hand-calculated WAC/carry, five-way cent rounding,
customer allocations, zero stock/shipments, empty sales, all-defective batches,
opening-stock shipments alongside new production losses, component corruption,
partial schemas, freight-once identities and input/sales permutation. Existing
purchasing, raw-material, production and financial tests remain non-destructive.
Small fixtures are generated only in memory; full pipeline/export entry points
are never invoked.

## Phase 6 outbound freight and operating-expense classification

Implementation version: `outbound-v1`. Phase 1-5 selling prices, material/labor/
energy rates, inbound freight, manufacturing overhead, fixed operating expense
bases and variable selling percentages are unchanged. Outbound costs are new
explicit service assumptions, not calculated from a desired margin. No actual
carrier quotes or achieved profitability are claimed.

### External outbound transport rates

| Customer segment | Base EUR/shipped unit | Fictional service assumption |
|---|---:|---|
| OEM | 1.20 | Consolidated scheduled industrial deliveries |
| Tier 1 | 1.50 | More frequent mixed industrial consignments |
| Aftermarket | 2.20 | Smaller packed consignments and more stops |

These are blended external carrier costs for delivering the modeled intermediate
subassemblies. Packaging/plant handling remains in the existing manufacturing
resource scope; no second packing/handling charge is added. Freight excludes
recoverable VAT, customs, storage, customer returns and inbound transport.
There is no customer freight recharge or separate delivery revenue. This first
model simplifies weight, geography, minimum consignment fees and carrier contracts;
per-unit costing should not be interpreted as a real parcel quote for one unit.

```text
Booked outbound EUR/unit = round(segment base * customer factor * month factor, 4)
```

Customer factor is 0.95-1.05; customer/month factor is 0.97-1.03. SHA-256 keys
include `outbound-v1`, seed label 362, segment, customer_id, and month_id for the
month factor. Approximate envelopes before rounding are EUR 1.1058-1.2978 (OEM),
1.38225-1.62225 (Tier 1), and 2.0273-2.3793 (Aftermarket). This is stable variation,
not an additional random draw or escalation assumption. Unknown segments and
nonpositive/nonfinite configured base rates are rejected. Existing sales RNG,
request fulfillment order, price variation and discounts are unchanged.

### Shipment recognition and schema

sales.csv appends exactly:

- `outbound_freight_rate_eur_per_unit` (four-decimal EUR/unit)
- `outbound_freight_eur` (booked shipment expense, two-decimal EUR)

```text
Outbound freight = round_half_up(units_shipped * outbound EUR/unit, 2)
```

Use Decimal multiplication with commercial half-up cent rounding. Neither
requested_units nor unfulfilled_units is a freight driver. Zero shipped units
produce zero freight, including at positive rates; normal sales generation
retains only fulfilled rows. An empty sales table still contains both new
numeric columns. No minimum shipment charge is modeled. Freight is recognized
in the sales shipment month and is never included in component manufacturing
COGS, finished-goods additions or raw-material value.

The expense is owned ONLY by sales. Do not copy it into operating_expenses.csv,
manufacturing_costs.csv, production_cost_allocation.csv or FG inventory. Existing
inbound freight already reaches manufacturing COGS through its own component;
its expense must not be repeated as outbound freight.

### Explicit operating expenses

operating_expenses.csv keeps the unchanged month/category grain and only the
existing categories `selling` and `administration`. Phase 6 appends
`variable_amount_eur`. Existing amount_eur, fixed_amount_eur, variable_rate_pct
and variable_driver_amount_eur retain their meanings. Rates use percentage
points: 2.0 means 2%, not 200%.

```text
Monthly escalation = 1 + 0.0015 * elapsed sorted calendar month index
Selling fixed = round_half_up(26000 * monthly escalation, 2)
Selling variable = round_half_up(net revenue * 0.02, 2)
Selling expenses = selling fixed + selling variable
Administration fixed = round_half_up(38000 * monthly escalation, 2)
Administration variable = 0
Administrative expenses = administration fixed
```

For selling, variable_driver_amount_eur is net revenue; for administration the
variable rate and driver amount are both zero. Fixed/variable parts are rounded
separately and amount_eur is their cent sum. Zero revenue removes variable
selling expense but leaves fixed selling/admin costs. Price changes would affect
net revenue and variable selling cost; freight depends on shipped units instead.
These relationships are tested, not exposed as a new What-if implementation.

Selling coverage remains commercial staff, office/customer service and
commissions/commercial support; it explicitly excludes freight. Administration
remains finance/HR/IT/management and services, excluding plant overhead. These
are shared company costs, not directly attributed product operating expenses.

### Company P&L contract

| Line | Authoritative source/calculation |
|---|---|
| Net Revenue | sales.net_revenue_eur |
| Manufacturing COGS | sales.cogs_eur, sum of five manufacturing components |
| Gross Profit | Net Revenue - Manufacturing COGS |
| Outbound Freight | sales.outbound_freight_eur |
| Selling Expenses | operating_expenses amount_eur for selling |
| Administrative Expenses | operating_expenses amount_eur for administration |
| Separately Expensed Production Costs | Idle line conversion expenses + zero-good-output production-loss expenses |
| Operating Profit | Gross Profit - Outbound Freight - Selling Expenses - Administrative Expenses - Separately Expensed Production Costs |

The production-expense line includes two distinct sources:
`manufacturing_costs.idle_cost_eur` for unused zero-attempt line pools, and
`production_cost_allocation.production_loss_expense_eur` for fully defective
batches (including their material and conversion components). They are deducted
below gross profit consistently with the existing policy. They are not COGS and
are not added to operating_expenses.csv. Ordinary partial defects remain in
capitalized good-unit cost as before.

`profit_totals` returns monetary amounts in integer cents. Existing keys revenue,
cogs, gross_profit, selling_admin_expenses, idle_cost, production_loss and
operating_profit remain. New keys are outbound_freight, selling_expenses,
administrative_expenses and separately_expensed_production_costs. The combined
selling_admin_expenses and separately_expensed_production_costs fields are aliases
for their constituent lines, not additional expenses. Never add an alias to its
parts. Generator CLI P&L output prints each deduction once, with idle and
production-loss expenses shown separately. Net income, interest, tax and cash
flows remain outside scope.

### Validation and compatibility

The financial validator recomputes segment/customer/month rates, shipment freight
amounts, fixed/variable expenses and monthly/company P&L in cents. It rejects
partial outbound schemas, invalid amounts, unknown expense categories, duplicate
sales/opex keys and outbound-owned columns appearing outside sales. Comparing
operating expense amounts to their resource/revenue formulas prevents freight
being hidden again inside selling/admin. Manufacturing source/FG/COGS component
validation prevents freight being inserted into manufacturing pools or inventory.

A completely pre-Phase-6 sales schema remains a legacy zero-outbound-freight
baseline for read-only validation/P&L. If either outbound field exists, both are
required. Legacy opex lacking variable_amount_eur can still be validated from
its existing fixed/rate/driver/amount fields; new generation always exports the
explicit variable amount. Removing both freight fields from a revised dataset
is NOT a migration technique: schema compatibility cannot recover omitted costs.
Phase 7 must require the complete revised schema before accepting new exports.

Tests include hand-calculated P&L, cent rounding, zero shipments/revenue,
segment variation, invalid/partial inputs, company/month sums, mixed production
losses, duplicate-cost rejection and historical compatibility. A freight-only
isolation test verifies that prices/revenue, all five manufacturing COGS
components, raw production, FG inventory and operating expenses remain unchanged;
operating profit changes by exactly outbound freight. No full generator or
export entry point is called; existing data/SQL/PBIX hashes are protected.

## Phase 7 controlled-regeneration handoff

Phase 7 completed on 24 October 2026 with a verified legacy backup, 61 passing
tests, strict exported-data validation and matching hashes for all 19 files in
an independent repeat run. Results: reports/phase7_20261024T141247792082+0200/.
Combined candidate gross margin is 23.338864% and operating margin 11.381570%;
no assumptions were changed after reviewing results. No promotion occurred.

The following controls govern any future controlled rebuild:

1. Authorize a coordinated run and choose staging/backup locations. Preserve the
   complete existing dataset and record source versions/seeds before overwriting.
2. Require complete Phase 1-6 schemas, not legacy compatibility paths, in staging.
   Rebuild masters, operations and financials together so BOMs, activity drivers,
   inbound components and FG/sales components refer to the same source version.
3. Validate exported CSVs after reading them back: keys/grains, all quantity/value
   roll-forwards, each cost component, shipment freight, opex and company P&L.
   Confirm deterministic rerun hashes and protection of raw/SQL/PBIX files.
4. Review realized product/month/company economics and the complete P&L. Document
   unexplained outliers; do not backsolve inputs from a target margin. Current
   tests establish arithmetic consistency, not a verified full-scale margin.
5. Review explicit PostgreSQL COPY columns/types and Power Query/DAX measures for
   additive fields, landed-material aliases, freight ownership and P&L aliases.
   Database/PBIX integration remains separately authorized work, not a side effect
   of regenerating CSVs.

Existing processed files remain entirely legacy. Phase 7 regenerated only a
separate staged candidate and its isolated repeat. No database migration, Power
BI change, candidate promotion or What-if engine has been performed. Remaining model limitations include blended per-unit
freight, no shipment geography/minimum charges, normal-capacity accounting,
machine-hour feasibility, material-specific FG lineage, demand elasticity and WIP.
