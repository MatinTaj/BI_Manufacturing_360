# PostgreSQL and Power BI migration readiness

Status: candidate CSVs are technically validated and deterministic; promotion,
database load and Power BI migration are NOT authorized or performed.

## Verified schema and row changes

All 19 legacy dataset filenames and all existing column names remain. New
fields are additive; none were removed. Exact ordered header lists are supplied
in schema_changes.json. Some retained fields have important expanded semantics.

| dataset | legacy_rows | candidate_rows | added_columns | removed_columns |
| --- | --- | --- | --- | --- |
| products | 20.00 | 20.00 | 2.00 | 0.00 |
| materials | 10.00 | 10.00 | 0.00 | 0.00 |
| suppliers | 15.00 | 15.00 | 0.00 | 0.00 |
| customers | 25.00 | 25.00 | 0.00 | 0.00 |
| production_lines | 3.00 | 3.00 | 2.00 | 0.00 |
| bom | 60.00 | 64.00 | 0.00 | 0.00 |
| material_suppliers | 30.00 | 30.00 | 0.00 | 0.00 |
| months | 24.00 | 24.00 | 0.00 | 0.00 |
| line_month_capacity | 72.00 | 72.00 | 0.00 | 0.00 |
| production | 480.00 | 480.00 | 0.00 | 0.00 |
| material_consumption | 1,440.00 | 1,536.00 | 4.00 | 0.00 |
| purchase_order_lines | 240.00 | 144.00 | 0.00 | 0.00 |
| material_receipts | 240.00 | 144.00 | 5.00 | 0.00 |
| raw_material_inventory | 240.00 | 240.00 | 11.00 | 0.00 |
| manufacturing_costs | 72.00 | 72.00 | 11.00 | 0.00 |
| production_cost_allocation | 480.00 | 480.00 | 16.00 | 0.00 |
| sales | 2,592.00 | 2,596.00 | 7.00 | 0.00 |
| finished_goods_inventory | 480.00 | 480.00 | 20.00 | 0.00 |
| operating_expenses | 48.00 | 48.00 | 4.00 | 0.00 |

BOM rows increase from 60 to 64, giving 1,536 consumption rows. Six materials
are used by the revised recipes; four catalog materials remain valid but unused,
so PO lines/receipts decrease from 240 to 144, with all 240 material/month
inventory snapshots retained. Sales lines change from 2,592 to 2,596.

Master product/material/supplier/customer/line ID domains and product-to-line
assignments were checked against legacy. Generated transaction IDs retain their
formats, but a repeated sequential ID is NOT a promise of the same legacy event.
Do not append/merge the new facts into old facts on these IDs; use one coherent
version of the candidate across all tables in an approved migration.

## Critical field meanings

- material_receipts.receipt_value_eur remains PURCHASE ONLY; purchase_value_eur
  aliases it. landed_receipt_value_eur includes inbound freight; landed_unit_cost_eur
  now means booked landed amount / received kg. It no longer equals PO unit price.
- raw_material_inventory.receipt_value_eur is also purchase-only. Its total value
  roll-forward must use landed_receipt_value_eur. Opening/issued/closing totals
  and weighted_average_unit_cost_eur are LANDED values, with separate components.
- material_consumption.issued_material_value_eur remains the LANDED issue total;
  its purchase/freight parts must not be added again to that total.
- production_cost_allocation.material_cost_eur remains the LANDED material subtotal.
  Sum purchase_material_cost_eur, inbound_freight_cost_eur, labor_cost_eur,
  energy_cost_eur and manufacturing_overhead_eur for the manufacturing total.
  Do not sum the landed subtotal together with its two parts.
- Sales material_cogs_eur is PURCHASE MATERIAL ONLY; it excludes inbound freight.
  cogs_eur is the sum of all five components. Component rounding is authoritative,
  so do not replace COGS with a separately rounded aggregate unit cost times units.
- sales.outbound_freight_eur is a distribution expense below gross profit, sourced
  once from sales; it is neither manufacturing COGS nor operating_expenses.csv.
- operating_expenses keeps exactly selling and administration categories. Rate
  2.0 means 2 percentage points; fixed + explicit variable amounts = amount_eur.
  Do not sum those two parts together with amount_eur again.

## PostgreSQL import requirements before approval

1. Prepare an isolated versioned candidate schema/table set; do not issue live
   ALTER/DELETE/TRUNCATE/INSERT/COPY until separately authorized.
2. Use explicit ordered COPY column lists for every CSV. Positional imports into
   old table schemas will fail on the added columns. Do not depend on SELECT *
   output order. Review database constraints/load ordering with the actual schema;
   no live database introspection was performed in this phase.
3. Use text for stable business IDs, date for month/order/receipt/shipment dates,
   integers for finished units, numeric(18,3) for kg, numeric(18,2) for booked money,
   numeric(18,4) for four-decimal tariffs/drivers and numeric(18,8) for unit costs.
   Avoid floating-point money and premature rounding of informational unit costs.
4. Load dimensions/masters first, then calendar/capacity/production, consumption
   and purchasing/inventory facts, then financial facts. PO lines must precede
   receipt foreign keys. Apply the documented PK/FK/composite grain constraints.
5. Re-run independent SQL totals against financial_comparison.csv and all cost/
   inventory component identities. Explicitly check logistics ownership and
   opening/closing snapshots. Keep candidate and legacy comparisons versioned.

The existing sql/production_analysis.sql references product_id/product_name,
production attempted/defective units and its existing product join. These columns
and grains are unchanged, so it remains structurally compatible; results will
change because this is a new synthetic dataset. It was inspected read-only and
was not executed against PostgreSQL or modified. Other external queries were
not available for review.

## Power BI relationship and measure implications

- Reuse Product, Material, Supplier, Customer, Production Line and Date dimensions;
  added cost columns do not need new relationships. Keep dimension-to-fact filters
  one-to-many and avoid ambiguous Product/Line filter paths.
- Keep BOM/approved suppliers as bridges. Never flatten BOM or material consumption
  onto sales rows without aggregation; it multiplies revenue and COGS.
- Preserve fact grains: sales_line_id; production_id; line/month cost pool;
  product/month FG; material/month RM; month/expense category. Use dimensions,
  not unrestricted bidirectional fact-to-fact relationships.
- A real role-playing Date dimension must include December 2023 order dates as
  well as 2024-25 receipts/shipments. Month keys are first-of-month. Use explicit
  active/inactive date roles for orders/receipts/shipments if required.
- Inventory snapshots are semi-additive: select end-of-period balances rather
  than summing closing values over months. Flow components and COGS are additive.
- Gross profit = net revenue - manufacturing COGS. Operating profit additionally
  subtracts outbound freight, selling, administration, idle-line expense and
  production-loss expense. Do not subtract purchases/production costs again.
- Margins use summed profit / summed revenue. Product gross/contribution after
  outbound is supported; product operating profit requires an explicit shared-
  expense allocation policy and must be labeled accordingly.
- Update Power Query column-selection/type steps and financial measures for all
  added columns and changed landed semantics. Do not format variable_rate_pct=2.0
  directly as a fraction-based percentage without dividing by 100.

Read-only PBIX archive inspection found diagram entries for public production
and public products and one visible Total Production card. The embedded binary
DataModel was not decoded, so hidden tables, relationships, DAX and data-source
bindings are NOT certified. A complete Desktop/semantic-model review and refresh
comparison is required before migration approval. The PBIX is unchanged.

## Acceptance decision

Ready for candidate approval/domain review: yes. Ready for automatic production
replacement or a certified SQL/Power BI migration: no. All schema mappings, live
constraints, DAX/relationship checks and an explicitly approved version-switch/
rollback procedure must be completed first. No promotion command is included.
