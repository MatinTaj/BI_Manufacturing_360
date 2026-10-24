> Phase 8B update: the live target is the existing database `manufacturing_360`, schema `manufacturing_v2`. Translate erp.X to manufacturing_v2.X, bi.X to manufacturing_v2.bi_X, and audit.X to manufacturing_v2.audit_X. See [active migration](../sql/v2/existing_schema/README.md) and [Power BI connection guide](power_bi_v2_connection.md). The separate-database descriptions below are Phase 8A history.

# Future Power BI v2 model

Recommendation only; no Power BI file was edited. Build a separate v2 model after authorized database validation, preserving legacy reports.

Use conformed product, customer, material, supplier, line and date/month dimensions. Preserve text IDs. A day calendar must cover purchasing dates as well as sales (including December 2023 where applicable). Monthly facts need a unique month dimension/bridge; first-of-month month_id is not a daily event date.

Use single-direction dimension-to-fact one-to-many relationships. Facts have separate grains: shipments, production batches, allocations, line/month pools, batch/material issues, PO lines, receipts, material/month and product/month snapshots, month/category opex. Do not create direct fact-to-fact or automatic bidirectional relationships. Composite grains need deliberate unique key mappings. BOM and approved suppliers are scoped bridges, not general filter paths through every fact. Avoid ambiguous line→product→fact and direct line→fact paths. Order and receipt dates require role-playing or deliberately inactive relationships.

Monthly P&L can be a separate summary fact or measures calculated from detailed facts, never both added together. Treat period_pnl as a reconciliation query: combined and annual rows overlap. Customer/product aggregate views are alternatives to detail, not additional revenue facts.

Use five authoritative COGS components. Gross profit = revenue − COGS; operating profit additionally subtracts outbound freight, selling, administration, idle and abnormal losses once. Product contribution after freight is not company operating profit. Do not invent shared expense allocations. Calculate margin totals as DIVIDE(summed profit, summed revenue), not averages. Keep pool costs and allocations separate. Never add landed material aggregate to purchase/freight components.

Inventory is semi-additive: sum across products/materials at one month end, never across closing months. Rates, ratios and weighted-average unit costs are not additive. Money can use Fixed Decimal Currency; activity, kg and eight-decimal unit costs need suitable precision rather than blanket Currency conversion.

Future What-if measures may apply independent sensitivity to recognized COGS components, net prices and outbound freight. Label this historical sensitivity, not a recalculated inventory forecast. Fixed selling/admin should remain fixed; revenue-variable selling responds to revised revenue. Separate support labor from activity labor and standby energy from activity energy when interpreting rate changes. Full prospective scenarios require time-phased purchasing, inventory turnover and capacity calculations. No new scenarios are implemented here.

Before switching reports, reconcile 2024, 2025 and combined P&L to Phase 7; verify monthly snapshots, zero denominators, discount semantics and slicers without duplicated BOM/supplier totals. Review old imports for positional columns, SELECT *, landed material semantics and omitted freight/production expenses. Do not replace reports automatically.
