-- Analytical results derive only from imported facts; no baseline constants.

-- Grain: one production_id (one product/month).
CREATE VIEW manufacturing_v2.bi_production_performance AS
SELECT p.production_id, p.month_id, m.year, m.quarter, p.product_id,
       d.product_name, d.category, d.line_id, p.attempted_units, p.defective_units, p.good_units,
       100.0*p.defective_units/nullif(p.attempted_units,0) AS defect_rate_pct,
       100.0*p.good_units/nullif(p.attempted_units,0) AS good_yield_pct
FROM manufacturing_v2.production p JOIN manufacturing_v2.products d ON d.product_id=p.product_id
JOIN manufacturing_v2.months m ON m.month_id=p.month_id;

-- Grain: line/month; production is aggregated before the capacity join.
CREATE VIEW manufacturing_v2.bi_line_production_performance AS
WITH p AS (
    SELECT month_id, line_id, sum(attempted_units) AS attempted_units,
           sum(defective_units) AS defective_units, sum(good_units) AS good_units
    FROM manufacturing_v2.bi_production_performance GROUP BY month_id,line_id
)
SELECT c.month_id,c.line_id,l.line_name,c.nominal_capacity_units,c.effective_capacity_units,c.downtime_pct,
       coalesce(p.attempted_units,0) AS attempted_units,coalesce(p.defective_units,0) AS defective_units,
       coalesce(p.good_units,0) AS good_units,
       100.0*p.attempted_units/nullif(c.effective_capacity_units,0) AS capacity_utilization_pct,
       100.0*p.defective_units/nullif(p.attempted_units,0) AS defect_rate_pct
FROM manufacturing_v2.line_month_capacity c JOIN manufacturing_v2.production_lines l ON l.line_id=c.line_id
LEFT JOIN p ON p.month_id=c.month_id AND p.line_id=c.line_id;

-- Grain: one production_id; landed subtotal and parts must not be added together.
CREATE VIEW manufacturing_v2.bi_manufacturing_cost_components AS
SELECT a.production_id,
       a.month_id,
       a.product_id,
       a.line_id,
       a.attempted_units,
       a.good_units,
       a.material_cost_eur,
       a.labor_cost_eur,
       a.energy_cost_eur,
       a.manufacturing_overhead_eur,
       a.total_manufacturing_cost_eur,
       a.capitalized_production_cost_eur,
       a.production_loss_expense_eur,
       a.good_unit_manufacturing_cost_eur,
       a.production_labor_cost_eur,
       a.support_labor_cost_eur,
       a.activity_energy_cost_eur,
       a.standby_energy_cost_eur,
       a.purchase_material_cost_eur,
       a.inbound_freight_cost_eur,
       a.capitalized_material_cost_eur,
       a.capitalized_inbound_freight_cost_eur,
       a.capitalized_labor_cost_eur,
       a.capitalized_energy_cost_eur,
       a.capitalized_overhead_cost_eur,
       a.material_production_loss_expense_eur,
       a.inbound_freight_production_loss_expense_eur,
       a.labor_production_loss_expense_eur,
       a.energy_production_loss_expense_eur,
       a.overhead_production_loss_expense_eur,
       p.product_name,p.category,
       a.material_cost_eur AS landed_material_cost_eur
FROM manufacturing_v2.production_cost_allocation a JOIN manufacturing_v2.products p ON p.product_id=a.product_id;

-- Grain: line/month cost pools; not additional to product cost allocations.
CREATE VIEW manufacturing_v2.bi_line_manufacturing_costs AS
SELECT c.month_id,
       c.line_id,
       c.attempted_units,
       c.labor_hours,
       c.hourly_rate_eur,
       c.energy_kwh,
       c.energy_tariff_eur,
       c.labor_cost_eur,
       c.energy_cost_eur,
       c.manufacturing_overhead_eur,
       c.total_conversion_cost_eur,
       c.idle_cost_eur,
       c.production_labor_hours,
       c.support_labor_hours,
       c.activity_energy_kwh,
       c.base_energy_kwh,
       c.production_labor_cost_eur,
       c.support_labor_cost_eur,
       c.activity_energy_cost_eur,
       c.standby_energy_cost_eur,
       c.idle_labor_cost_eur,
       c.idle_energy_cost_eur,
       c.idle_overhead_cost_eur, l.line_name
FROM manufacturing_v2.manufacturing_costs c JOIN manufacturing_v2.production_lines l ON l.line_id=c.line_id;

-- Grain: one sales_line_id; dimension joins only.
CREATE VIEW manufacturing_v2.bi_sales_detail AS
SELECT s.sales_line_id,
       s.month_id,
       s.shipment_date,
       s.product_id,
       s.customer_id,
       s.requested_units,
       s.unfulfilled_units,
       s.units_shipped,
       s.list_unit_price_eur,
       s.discount_pct,
       s.gross_revenue_eur,
       s.discount_amount_eur,
       s.net_revenue_eur,
       s.weighted_average_unit_cost_eur,
       s.cogs_eur,
       s.material_cogs_eur,
       s.inbound_freight_cogs_eur,
       s.labor_cogs_eur,
       s.energy_cogs_eur,
       s.overhead_cogs_eur,
       s.outbound_freight_rate_eur_per_unit,
       s.outbound_freight_eur,
       p.product_name,p.category,p.line_id,c.customer_name,c.segment,
       s.net_revenue_eur/nullif(s.units_shipped,0) AS net_unit_price_eur,
       s.net_revenue_eur-s.cogs_eur AS gross_profit_eur,
       100.0*(s.net_revenue_eur-s.cogs_eur)/nullif(s.net_revenue_eur,0) AS gross_margin_pct,
       s.net_revenue_eur-s.cogs_eur-s.outbound_freight_eur AS contribution_after_outbound_eur
FROM manufacturing_v2.sales s JOIN manufacturing_v2.products p ON p.product_id=s.product_id
JOIN manufacturing_v2.customers c ON c.customer_id=s.customer_id;

-- Grain: customer/month; no product-production facts joined.
CREATE VIEW manufacturing_v2.bi_customer_month_performance AS
SELECT month_id,customer_id,customer_name,segment,count(*) AS sales_lines,
       sum(units_shipped) AS units_shipped,sum(net_revenue_eur) AS net_revenue_eur,
       sum(cogs_eur) AS manufacturing_cogs_eur,sum(outbound_freight_eur) AS outbound_freight_eur,
       sum(net_revenue_eur-cogs_eur) AS gross_profit_eur,
       sum(net_revenue_eur-cogs_eur-outbound_freight_eur) AS contribution_after_outbound_eur,
       100.0*sum(net_revenue_eur-cogs_eur)/nullif(sum(net_revenue_eur),0) AS gross_margin_pct,
       sum(net_revenue_eur)/nullif(sum(units_shipped),0) AS net_asp_eur
FROM manufacturing_v2.bi_sales_detail GROUP BY month_id,customer_id,customer_name,segment;

-- Grain: product/month; one aggregate sales row joins one allocation and one FG row; no shared opex allocation.
CREATE VIEW manufacturing_v2.bi_product_month_profitability AS
WITH s AS (
    SELECT month_id,product_id,sum(units_shipped) AS units_shipped,sum(net_revenue_eur) AS net_revenue_eur,sum(cogs_eur) AS cogs_eur,sum(outbound_freight_eur) AS outbound_freight_eur,sum(material_cogs_eur) AS material_cogs_eur,sum(inbound_freight_cogs_eur) AS inbound_freight_cogs_eur,sum(labor_cogs_eur) AS labor_cogs_eur,sum(energy_cogs_eur) AS energy_cogs_eur,sum(overhead_cogs_eur) AS overhead_cogs_eur
    FROM manufacturing_v2.sales GROUP BY month_id,product_id
)
SELECT i.month_id,p.product_id,p.product_name,p.category,p.line_id,
       coalesce(s.units_shipped,0) AS units_shipped,
       coalesce(s.net_revenue_eur,0) AS net_revenue_eur,
       coalesce(s.cogs_eur,0) AS cogs_eur,
       coalesce(s.outbound_freight_eur,0) AS outbound_freight_eur,
       coalesce(s.material_cogs_eur,0) AS material_cogs_eur,
       coalesce(s.inbound_freight_cogs_eur,0) AS inbound_freight_cogs_eur,
       coalesce(s.labor_cogs_eur,0) AS labor_cogs_eur,
       coalesce(s.energy_cogs_eur,0) AS energy_cogs_eur,
       coalesce(s.overhead_cogs_eur,0) AS overhead_cogs_eur,
       coalesce(s.net_revenue_eur-s.cogs_eur,0) AS gross_profit_eur,
       coalesce(s.net_revenue_eur-s.cogs_eur-s.outbound_freight_eur,0) AS contribution_after_outbound_eur,
       100.0*(s.net_revenue_eur-s.cogs_eur)/nullif(s.net_revenue_eur,0) AS gross_margin_pct,
       a.total_manufacturing_cost_eur AS production_manufacturing_cost_eur,
       a.capitalized_production_cost_eur,a.production_loss_expense_eur,
       i.closing_units,i.closing_value_eur
FROM manufacturing_v2.finished_goods_inventory i JOIN manufacturing_v2.products p ON p.product_id=i.product_id
JOIN manufacturing_v2.production_cost_allocation a ON a.month_id=i.month_id AND a.product_id=i.product_id
LEFT JOIN s ON s.month_id=i.month_id AND s.product_id=i.product_id;

-- Grain: product across loaded periods; no inventory snapshots are summed.
CREATE VIEW manufacturing_v2.bi_product_profitability AS
SELECT product_id,product_name,category,line_id,
       sum(units_shipped) AS units_shipped,
       sum(net_revenue_eur) AS net_revenue_eur,
       sum(cogs_eur) AS cogs_eur,
       sum(outbound_freight_eur) AS outbound_freight_eur,
       sum(material_cogs_eur) AS material_cogs_eur,
       sum(inbound_freight_cogs_eur) AS inbound_freight_cogs_eur,
       sum(labor_cogs_eur) AS labor_cogs_eur,
       sum(energy_cogs_eur) AS energy_cogs_eur,
       sum(overhead_cogs_eur) AS overhead_cogs_eur,
       sum(gross_profit_eur) AS gross_profit_eur,
       sum(contribution_after_outbound_eur) AS contribution_after_outbound_eur,
       100.0*sum(gross_profit_eur)/nullif(sum(net_revenue_eur),0) AS gross_margin_pct,
       sum(net_revenue_eur)/nullif(sum(units_shipped),0) AS net_asp_eur
FROM manufacturing_v2.bi_product_month_profitability GROUP BY product_id,product_name,category,line_id;

-- Grain: material/month snapshot; balances are not additive across months.
CREATE VIEW manufacturing_v2.bi_raw_material_inventory AS
SELECT i.month_id,
       i.material_id,
       i.opening_kg,
       i.received_kg,
       i.consumed_kg,
       i.closing_kg,
       i.opening_value_eur,
       i.receipt_value_eur,
       i.issued_material_value_eur,
       i.closing_value_eur,
       i.weighted_average_unit_cost_eur,
       i.opening_purchase_material_value_eur,
       i.opening_inbound_freight_value_eur,
       i.receipt_purchase_material_value_eur,
       i.receipt_inbound_freight_value_eur,
       i.issued_purchase_material_value_eur,
       i.issued_inbound_freight_value_eur,
       i.closing_purchase_material_value_eur,
       i.closing_inbound_freight_value_eur,
       i.landed_receipt_value_eur,
       i.weighted_average_purchase_unit_cost_eur,
       i.weighted_average_inbound_freight_unit_cost_eur,m.material_name,m.unit
FROM manufacturing_v2.raw_material_inventory i JOIN manufacturing_v2.materials m ON m.material_id=i.material_id;

-- Grain: product/month snapshot; balances are not additive across months.
CREATE VIEW manufacturing_v2.bi_finished_goods_inventory AS
SELECT i.month_id,
       i.product_id,
       i.opening_units,
       i.good_production_units,
       i.demand_units,
       i.shipped_units,
       i.unfulfilled_units,
       i.closing_units,
       i.opening_value_eur,
       i.production_value_eur,
       i.cogs_eur,
       i.closing_value_eur,
       i.weighted_average_unit_cost_eur,
       i.opening_material_value_eur,
       i.opening_inbound_freight_value_eur,
       i.opening_labor_value_eur,
       i.opening_energy_value_eur,
       i.opening_overhead_value_eur,
       i.production_material_value_eur,
       i.production_inbound_freight_value_eur,
       i.production_labor_value_eur,
       i.production_energy_value_eur,
       i.production_overhead_value_eur,
       i.closing_material_value_eur,
       i.closing_inbound_freight_value_eur,
       i.closing_labor_value_eur,
       i.closing_energy_value_eur,
       i.closing_overhead_value_eur,
       i.material_cogs_eur,
       i.inbound_freight_cogs_eur,
       i.labor_cogs_eur,
       i.energy_cogs_eur,
       i.overhead_cogs_eur,p.product_name,p.category,p.line_id
FROM manufacturing_v2.finished_goods_inventory i JOIN manufacturing_v2.products p ON p.product_id=i.product_id;

-- Grain: receipt_id; no order quantity/value is repeated in receipt measures.
CREATE VIEW manufacturing_v2.bi_procurement_receipts AS
SELECT r.receipt_id,
       r.po_line_id,
       r.receipt_date,
       r.received_kg,
       r.landed_unit_cost_eur,
       r.receipt_value_eur,
       r.purchase_unit_cost_eur,
       r.purchase_value_eur,
       r.inbound_freight_rate_eur_per_kg,
       r.inbound_freight_eur,
       r.landed_receipt_value_eur,
       o.material_id,o.supplier_id,o.order_date,o.expected_receipt_date,o.agreed_unit_cost_eur,
       m.material_name,s.supplier_name,
       (r.receipt_date<=o.expected_receipt_date) AS on_time,
       r.receipt_date-o.order_date AS actual_lead_time_days
FROM manufacturing_v2.material_receipts r JOIN manufacturing_v2.purchase_order_lines o ON o.po_line_id=r.po_line_id
JOIN manufacturing_v2.materials m ON m.material_id=o.material_id
JOIN manufacturing_v2.suppliers s ON s.supplier_id=o.supplier_id;

-- Grain: po_line_id; receipt totals preaggregated to prevent order fan-out.
CREATE VIEW manufacturing_v2.bi_procurement_order_status AS
WITH r AS (
    SELECT po_line_id,sum(received_kg) AS received_kg,sum(purchase_value_eur) AS purchase_value_eur,
           sum(inbound_freight_eur) AS inbound_freight_eur,sum(landed_receipt_value_eur) AS landed_receipt_value_eur
    FROM manufacturing_v2.material_receipts GROUP BY po_line_id
)
SELECT o.po_line_id,o.material_id,o.supplier_id,o.order_date,o.expected_receipt_date,o.ordered_kg,
       o.agreed_unit_cost_eur,coalesce(r.received_kg,0) AS received_kg,
       o.ordered_kg-coalesce(r.received_kg,0) AS outstanding_kg,
       coalesce(r.purchase_value_eur,0) AS purchase_value_eur,
       coalesce(r.inbound_freight_eur,0) AS inbound_freight_eur,
       coalesce(r.landed_receipt_value_eur,0) AS landed_receipt_value_eur
FROM manufacturing_v2.purchase_order_lines o LEFT JOIN r ON r.po_line_id=o.po_line_id;

-- Grain: production_id/material_id; no join to sales.
CREATE VIEW manufacturing_v2.bi_material_consumption AS
SELECT c.production_id,
       c.material_id,
       c.required_kg,
       c.extra_waste_kg,
       c.consumed_kg,
       c.issued_material_value_eur,
       c.weighted_average_unit_cost_eur,
       c.issued_purchase_material_value_eur,
       c.issued_inbound_freight_eur,
       c.weighted_average_purchase_unit_cost_eur,
       c.weighted_average_inbound_freight_unit_cost_eur,p.month_id,p.product_id,d.product_name,m.material_name
FROM manufacturing_v2.material_consumption c JOIN manufacturing_v2.production p ON p.production_id=c.production_id
JOIN manufacturing_v2.products d ON d.product_id=p.product_id JOIN manufacturing_v2.materials m ON m.material_id=c.material_id;

-- Grain: month; each fact independently aggregated before joining; no hardcoded financial results.
CREATE VIEW manufacturing_v2.bi_monthly_pnl AS
WITH s AS (
    SELECT month_id,sum(net_revenue_eur) AS revenue,sum(cogs_eur) AS cogs,
           sum(outbound_freight_eur) AS outbound_freight
    FROM manufacturing_v2.sales GROUP BY month_id
), o AS (
    SELECT month_id,sum(amount_eur) FILTER (WHERE expense_category='selling') AS selling_expenses,
           sum(amount_eur) FILTER (WHERE expense_category='administration') AS administrative_expenses
    FROM manufacturing_v2.operating_expenses GROUP BY month_id
), idle AS (
    SELECT month_id,sum(idle_cost_eur) AS idle_cost FROM manufacturing_v2.manufacturing_costs GROUP BY month_id
), loss AS (
    SELECT month_id,sum(production_loss_expense_eur) AS production_loss
    FROM manufacturing_v2.production_cost_allocation GROUP BY month_id
), amounts AS (
    SELECT m.month_id,m.year,m.quarter,coalesce(s.revenue,0) AS revenue,coalesce(s.cogs,0) AS cogs,
           coalesce(s.outbound_freight,0) AS outbound_freight,coalesce(o.selling_expenses,0) AS selling_expenses,
           coalesce(o.administrative_expenses,0) AS administrative_expenses,coalesce(idle.idle_cost,0) AS idle_cost,
           coalesce(loss.production_loss,0) AS production_loss
    FROM manufacturing_v2.months m LEFT JOIN s ON s.month_id=m.month_id LEFT JOIN o ON o.month_id=m.month_id
    LEFT JOIN idle ON idle.month_id=m.month_id LEFT JOIN loss ON loss.month_id=m.month_id
), pnl AS (
    SELECT month_id,year,quarter,revenue,cogs,revenue-cogs AS gross_profit,outbound_freight,
           selling_expenses,administrative_expenses,idle_cost,production_loss,
           revenue-cogs-outbound_freight-selling_expenses-administrative_expenses-idle_cost-production_loss AS operating_profit
    FROM amounts
)
SELECT month_id,year,quarter,revenue,cogs,gross_profit,outbound_freight,selling_expenses,
       administrative_expenses,idle_cost,production_loss,operating_profit,
       100.0*gross_profit/nullif(revenue,0) AS gross_margin_pct,
       100.0*operating_profit/nullif(revenue,0) AS operating_margin_pct
FROM pnl;

-- Grain: year plus combined period; do not sum combined row with years.
CREATE VIEW manufacturing_v2.bi_period_pnl AS
SELECT CASE WHEN grouping(year)=1 THEN 'combined' ELSE year::text END AS period,
       sum(revenue) AS revenue,
       sum(cogs) AS cogs,
       sum(gross_profit) AS gross_profit,
       sum(outbound_freight) AS outbound_freight,
       sum(selling_expenses) AS selling_expenses,
       sum(administrative_expenses) AS administrative_expenses,
       sum(idle_cost) AS idle_cost,
       sum(production_loss) AS production_loss,
       sum(operating_profit) AS operating_profit,
       100.0*sum(gross_profit)/nullif(sum(revenue),0) AS gross_margin_pct,
       100.0*sum(operating_profit)/nullif(sum(revenue),0) AS operating_margin_pct
FROM manufacturing_v2.bi_monthly_pnl GROUP BY GROUPING SETS ((year),());
