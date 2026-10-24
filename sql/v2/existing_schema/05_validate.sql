-- Cross-table reconciliations. Every query returns failure counts; any failure aborts the migration transaction.
CREATE VIEW manufacturing_v2.audit_pnl_reconciliation AS
SELECT coalesce(e.period,a.period) AS period,v.metric,v.expected,v.actual,
       v.actual-v.expected AS difference,
       (v.expected IS NOT NULL AND v.actual IS NOT NULL AND abs(v.actual-v.expected)<=v.tolerance) AS passed
FROM manufacturing_v2.audit_expected_pnl e FULL JOIN manufacturing_v2.bi_period_pnl a USING(period)
CROSS JOIN LATERAL (VALUES ('revenue',e.revenue,a.revenue,0::numeric),('cogs',e.cogs,a.cogs,0::numeric),('gross_profit',e.gross_profit,a.gross_profit,0::numeric),('outbound_freight',e.outbound_freight,a.outbound_freight,0::numeric),('selling_expenses',e.selling_expenses,a.selling_expenses,0::numeric),('administrative_expenses',e.administrative_expenses,a.administrative_expenses,0::numeric),('idle_cost',e.idle_cost,a.idle_cost,0::numeric),('production_loss',e.production_loss,a.production_loss,0::numeric),('operating_profit',e.operating_profit,a.operating_profit,0::numeric),('gross_margin_pct',e.gross_margin_pct,a.gross_margin_pct,0.00000001::numeric),('operating_margin_pct',e.operating_margin_pct,a.operating_margin_pct,0.00000001::numeric)) v(metric,expected,actual,tolerance);

CREATE VIEW manufacturing_v2.audit_validation_results AS
SELECT 'expected_file_catalog'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT 1 WHERE (SELECT count(*) FROM manufacturing_v2.audit_expected_files) <> 19) failures
UNION ALL
SELECT 'row_counts'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH actual AS (SELECT 'months'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.months UNION ALL SELECT 'production_lines'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.production_lines UNION ALL SELECT 'materials'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.materials UNION ALL SELECT 'suppliers'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.suppliers UNION ALL SELECT 'customers'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.customers UNION ALL SELECT 'products'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.products UNION ALL SELECT 'material_suppliers'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.material_suppliers UNION ALL SELECT 'bom'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.bom UNION ALL SELECT 'line_month_capacity'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.line_month_capacity UNION ALL SELECT 'production'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.production UNION ALL SELECT 'purchase_order_lines'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.purchase_order_lines UNION ALL SELECT 'material_receipts'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.material_receipts UNION ALL SELECT 'material_consumption'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.material_consumption UNION ALL SELECT 'raw_material_inventory'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.raw_material_inventory UNION ALL SELECT 'manufacturing_costs'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.manufacturing_costs UNION ALL SELECT 'production_cost_allocation'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.production_cost_allocation UNION ALL SELECT 'finished_goods_inventory'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.finished_goods_inventory UNION ALL SELECT 'sales'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.sales UNION ALL SELECT 'operating_expenses'::text AS dataset,count(*)::bigint AS row_count FROM manufacturing_v2.operating_expenses) SELECT coalesce(e.dataset,a.dataset) FROM manufacturing_v2.audit_expected_files e FULL JOIN actual a USING(dataset) WHERE e.row_count IS DISTINCT FROM a.row_count) failures
UNION ALL
SELECT 'calendar'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT month_id FROM manufacturing_v2.months WHERE month_id < DATE '2024-01-01' OR month_id > DATE '2025-12-01') failures
UNION ALL
SELECT 'allocation_source_quantities'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT a.production_id FROM manufacturing_v2.production_cost_allocation a JOIN manufacturing_v2.production p USING(production_id) WHERE a.attempted_units<>p.attempted_units OR a.good_units<>p.good_units) failures
UNION ALL
SELECT 'bom_consumption'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT c.production_id FROM manufacturing_v2.material_consumption c JOIN manufacturing_v2.production p USING(production_id) LEFT JOIN manufacturing_v2.bom b ON b.product_id=p.product_id AND b.material_id=c.material_id WHERE b.product_id IS NULL OR c.required_kg<>round(p.attempted_units*b.quantity_kg_per_unit,3)) failures
UNION ALL
SELECT 'missing_bom_consumption'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT p.production_id FROM manufacturing_v2.production p JOIN manufacturing_v2.bom b USING(product_id) LEFT JOIN manufacturing_v2.material_consumption c ON c.production_id=p.production_id AND c.material_id=b.material_id WHERE c.production_id IS NULL) failures
UNION ALL
SELECT 'allocation_material_sources'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH c AS (SELECT production_id,sum(issued_purchase_material_value_eur) AS purchase,sum(issued_inbound_freight_eur) AS freight FROM manufacturing_v2.material_consumption GROUP BY production_id)
SELECT a.production_id FROM manufacturing_v2.production_cost_allocation a LEFT JOIN c USING(production_id)
WHERE a.purchase_material_cost_eur<>coalesce(c.purchase,0) OR a.inbound_freight_cost_eur<>coalesce(c.freight,0)) failures
UNION ALL
SELECT 'line_capacity_and_cost_attempts'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH p AS (SELECT p.month_id,d.line_id,sum(p.attempted_units) AS attempted FROM manufacturing_v2.production p JOIN manufacturing_v2.products d USING(product_id) GROUP BY p.month_id,d.line_id)
SELECT c.month_id FROM manufacturing_v2.line_month_capacity c JOIN manufacturing_v2.manufacturing_costs m USING(month_id,line_id) LEFT JOIN p USING(month_id,line_id)
WHERE coalesce(p.attempted,0)>c.effective_capacity_units OR m.attempted_units<>coalesce(p.attempted,0)) failures
UNION ALL
SELECT 'conversion_pool_conservation'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH a AS (SELECT month_id,line_id,sum(labor_cost_eur) AS labor_cost_eur,sum(energy_cost_eur) AS energy_cost_eur,sum(manufacturing_overhead_eur) AS manufacturing_overhead_eur FROM manufacturing_v2.production_cost_allocation GROUP BY month_id,line_id) SELECT m.month_id FROM manufacturing_v2.manufacturing_costs m LEFT JOIN a USING(month_id,line_id) WHERE m.labor_cost_eur<>coalesce(a.labor_cost_eur,0)+m.idle_labor_cost_eur OR m.energy_cost_eur<>coalesce(a.energy_cost_eur,0)+m.idle_energy_cost_eur OR m.manufacturing_overhead_eur<>coalesce(a.manufacturing_overhead_eur,0)+m.idle_overhead_cost_eur) failures
UNION ALL
SELECT 'activity_allocation_cents'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH activity AS (
 SELECT a.*,d.standard_labor_hours_per_attempt*a.attempted_units AS hours,
        d.standard_energy_kwh_per_attempt*a.attempted_units AS kwh
 FROM manufacturing_v2.production_cost_allocation a JOIN manufacturing_v2.products d USING(product_id)
), pools AS (
 SELECT a.month_id,a.line_id,a.production_id,v.pool,v.amount*100 AS cents,v.actual*100 AS actual,
        v.driver,v.fixed,a.attempted_units
 FROM activity a JOIN manufacturing_v2.manufacturing_costs m USING(month_id,line_id)
 CROSS JOIN LATERAL (VALUES
 ('production_labor',m.production_labor_cost_eur,a.production_labor_cost_eur,a.hours,false),
 ('support_labor',m.support_labor_cost_eur,a.support_labor_cost_eur,a.hours,true),
 ('activity_energy',m.activity_energy_cost_eur,a.activity_energy_cost_eur,a.kwh,false),
 ('standby_energy',m.standby_energy_cost_eur,a.standby_energy_cost_eur,a.kwh,true),
 ('overhead',m.manufacturing_overhead_eur,a.manufacturing_overhead_eur,a.hours,true)
 ) v(pool,amount,actual,driver,fixed)
), weights AS (
 SELECT month_id,line_id,production_id,pool,cents,actual,
 CASE WHEN fixed AND sum(driver) OVER (PARTITION BY month_id,line_id,pool)=0 THEN attempted_units ELSE driver END AS weight
 FROM pools
), totals AS (
 SELECT month_id,line_id,production_id,pool,cents,actual,weight,
 sum(weight) OVER (PARTITION BY month_id,line_id,pool) AS denominator FROM weights
), portions AS (
 SELECT month_id,line_id,production_id,pool,cents,actual,weight,
 coalesce(floor(cents*weight/nullif(denominator,0)),0) AS initial,
 coalesce(mod(cents*weight,nullif(denominator,0)),0) AS remainder FROM totals
), ranked AS (
 SELECT month_id,line_id,production_id,pool,cents,actual,weight,initial,
 cents-sum(initial) OVER (PARTITION BY month_id,line_id,pool) AS residual,
 row_number() OVER (PARTITION BY month_id,line_id,pool ORDER BY remainder DESC,production_id) AS priority
 FROM portions
) SELECT production_id,pool FROM ranked WHERE actual<>initial+CASE WHEN weight>0 AND priority<=residual THEN 1 ELSE 0 END) failures
UNION ALL
SELECT 'production_activity_drivers'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH a AS (
SELECT p.month_id,d.line_id,sum(p.attempted_units*d.standard_labor_hours_per_attempt) AS hours,
 sum(p.attempted_units*d.standard_energy_kwh_per_attempt) AS kwh
FROM manufacturing_v2.production p JOIN manufacturing_v2.products d USING(product_id) GROUP BY p.month_id,d.line_id)
SELECT m.month_id FROM manufacturing_v2.manufacturing_costs m LEFT JOIN a USING(month_id,line_id) JOIN manufacturing_v2.production_lines l USING(line_id)
WHERE abs(m.production_labor_hours-coalesce(a.hours,0))>0.005001
OR abs(m.activity_energy_kwh-coalesce(a.kwh,0))>0.005001
OR m.support_labor_hours<>l.support_labor_hours_per_month OR m.base_energy_kwh<>l.base_energy_kwh_per_month) failures
UNION ALL
SELECT 'conversion_subpool_valuation'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT month_id FROM manufacturing_v2.manufacturing_costs WHERE production_labor_cost_eur<>round(production_labor_hours*hourly_rate_eur,2) OR activity_energy_cost_eur<>round(activity_energy_kwh*energy_tariff_eur,2)) failures
UNION ALL
SELECT 'receipt_po_terms'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT r.receipt_id FROM manufacturing_v2.material_receipts r JOIN manufacturing_v2.purchase_order_lines p USING(po_line_id) JOIN manufacturing_v2.suppliers s USING(supplier_id) WHERE r.received_kg<>p.ordered_kg OR r.purchase_unit_cost_eur<>p.agreed_unit_cost_eur OR r.receipt_date<>p.expected_receipt_date OR r.receipt_date-p.order_date<>s.lead_time_days OR extract(day FROM r.receipt_date)<>25) failures
UNION ALL
SELECT 'orders_fully_received'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT p.po_line_id FROM manufacturing_v2.purchase_order_lines p LEFT JOIN manufacturing_v2.material_receipts r USING(po_line_id) WHERE r.receipt_id IS NULL) failures
UNION ALL
SELECT 'raw_receipt_flows'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH r AS (SELECT date_trunc('month',r.receipt_date)::date AS month_id,p.material_id,
sum(r.received_kg) AS kg,sum(r.purchase_value_eur) AS purchase,sum(r.inbound_freight_eur) AS freight
FROM manufacturing_v2.material_receipts r JOIN manufacturing_v2.purchase_order_lines p USING(po_line_id) GROUP BY 1,2)
SELECT coalesce(i.month_id,r.month_id) FROM manufacturing_v2.raw_material_inventory i FULL JOIN r USING(month_id,material_id)
WHERE i.month_id IS NULL OR i.received_kg<>coalesce(r.kg,0) OR i.receipt_purchase_material_value_eur<>coalesce(r.purchase,0) OR i.receipt_inbound_freight_value_eur<>coalesce(r.freight,0)) failures
UNION ALL
SELECT 'raw_issue_flows'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH c AS (SELECT p.month_id,c.material_id,sum(c.consumed_kg) AS kg,
sum(c.issued_purchase_material_value_eur) AS purchase,sum(c.issued_inbound_freight_eur) AS freight
FROM manufacturing_v2.material_consumption c JOIN manufacturing_v2.production p USING(production_id) GROUP BY 1,2)
SELECT coalesce(i.month_id,c.month_id) FROM manufacturing_v2.raw_material_inventory i FULL JOIN c USING(month_id,material_id)
WHERE i.month_id IS NULL OR i.consumed_kg<>coalesce(c.kg,0) OR i.issued_purchase_material_value_eur<>coalesce(c.purchase,0) OR i.issued_inbound_freight_value_eur<>coalesce(c.freight,0)) failures
UNION ALL
SELECT 'raw_wac_purchase_material'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT month_id FROM manufacturing_v2.raw_material_inventory WHERE issued_purchase_material_value_eur<>coalesce(round((opening_purchase_material_value_eur+receipt_purchase_material_value_eur)*consumed_kg/nullif(opening_kg+received_kg,0),2),0)) failures
UNION ALL
SELECT 'raw_wac_inbound_freight'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT month_id FROM manufacturing_v2.raw_material_inventory WHERE issued_inbound_freight_value_eur<>coalesce(round((opening_inbound_freight_value_eur+receipt_inbound_freight_value_eur)*consumed_kg/nullif(opening_kg+received_kg,0),2),0)) failures
UNION ALL
SELECT 'raw_carry_forward'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH x AS (SELECT month_id,material_id,row_number() OVER (PARTITION BY material_id ORDER BY month_id) AS rn,opening_kg IS DISTINCT FROM lag(closing_kg) OVER (PARTITION BY material_id ORDER BY month_id) AS bad_0,opening_value_eur IS DISTINCT FROM lag(closing_value_eur) OVER (PARTITION BY material_id ORDER BY month_id) AS bad_1,opening_purchase_material_value_eur IS DISTINCT FROM lag(closing_purchase_material_value_eur) OVER (PARTITION BY material_id ORDER BY month_id) AS bad_2,opening_inbound_freight_value_eur IS DISTINCT FROM lag(closing_inbound_freight_value_eur) OVER (PARTITION BY material_id ORDER BY month_id) AS bad_3 FROM manufacturing_v2.raw_material_inventory) SELECT month_id FROM x WHERE rn>1 AND (bad_0 OR bad_1 OR bad_2 OR bad_3)) failures
UNION ALL
SELECT 'raw_issue_cent_allocation'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH pool AS (
SELECT p.month_id,c.material_id,c.production_id,c.consumed_kg*1000 AS weight,v.component,v.cents,v.actual
FROM manufacturing_v2.material_consumption c JOIN manufacturing_v2.production p USING(production_id)
JOIN manufacturing_v2.raw_material_inventory i ON i.month_id=p.month_id AND i.material_id=c.material_id
CROSS JOIN LATERAL (VALUES
('purchase',i.issued_purchase_material_value_eur*100,c.issued_purchase_material_value_eur*100),
('freight',i.issued_inbound_freight_value_eur*100,c.issued_inbound_freight_eur*100)) v(component,cents,actual)
), totals AS (
SELECT month_id,material_id,production_id,weight,component,cents,actual,sum(weight) OVER (PARTITION BY month_id,material_id,component) AS denominator FROM pool
), initial AS (
SELECT month_id,material_id,production_id,weight,component,cents,actual,
coalesce(floor(cents*weight/nullif(denominator,0)),0) AS base,
coalesce(mod(cents*weight,nullif(denominator,0)),0) AS remainder FROM totals
), ranked AS (
SELECT production_id,weight,component,actual,base,cents-sum(base) OVER (PARTITION BY month_id,material_id,component) AS residual,
row_number() OVER (PARTITION BY month_id,material_id,component ORDER BY remainder DESC,production_id) AS priority FROM initial
) SELECT production_id,component FROM ranked WHERE actual<>base+CASE WHEN weight>0 AND priority<=residual THEN 1 ELSE 0 END) failures
UNION ALL
SELECT 'fg_capitalized_sources'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT i.product_id FROM manufacturing_v2.finished_goods_inventory i JOIN manufacturing_v2.production_cost_allocation a USING(month_id,product_id) WHERE i.good_production_units<>a.good_units OR i.production_material_value_eur<>a.capitalized_material_cost_eur OR i.production_inbound_freight_value_eur<>a.capitalized_inbound_freight_cost_eur OR i.production_labor_value_eur<>a.capitalized_labor_cost_eur OR i.production_energy_value_eur<>a.capitalized_energy_cost_eur OR i.production_overhead_value_eur<>a.capitalized_overhead_cost_eur) failures
UNION ALL
SELECT 'fg_carry_and_initial_zero'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH x AS (SELECT i.*,row_number() OVER w AS rn,lag(closing_units) OVER w AS previous_units,lag(closing_material_value_eur) OVER w AS previous_material,lag(closing_inbound_freight_value_eur) OVER w AS previous_inbound_freight,lag(closing_labor_value_eur) OVER w AS previous_labor,lag(closing_energy_value_eur) OVER w AS previous_energy,lag(closing_overhead_value_eur) OVER w AS previous_overhead FROM manufacturing_v2.finished_goods_inventory i WINDOW w AS (PARTITION BY product_id ORDER BY month_id)) SELECT product_id FROM x WHERE (rn=1 AND (opening_units<>0 OR opening_value_eur<>0)) OR (rn>1 AND (opening_units<>previous_units OR opening_material_value_eur<>previous_material OR opening_inbound_freight_value_eur<>previous_inbound_freight OR opening_labor_value_eur<>previous_labor OR opening_energy_value_eur<>previous_energy OR opening_overhead_value_eur<>previous_overhead))) failures
UNION ALL
SELECT 'fg_wac_material'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT product_id FROM manufacturing_v2.finished_goods_inventory WHERE material_cogs_eur<>coalesce(round((opening_material_value_eur+production_material_value_eur)*shipped_units/nullif(opening_units+good_production_units,0),2),0)) failures
UNION ALL
SELECT 'fg_wac_inbound_freight'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT product_id FROM manufacturing_v2.finished_goods_inventory WHERE inbound_freight_cogs_eur<>coalesce(round((opening_inbound_freight_value_eur+production_inbound_freight_value_eur)*shipped_units/nullif(opening_units+good_production_units,0),2),0)) failures
UNION ALL
SELECT 'fg_wac_labor'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT product_id FROM manufacturing_v2.finished_goods_inventory WHERE labor_cogs_eur<>coalesce(round((opening_labor_value_eur+production_labor_value_eur)*shipped_units/nullif(opening_units+good_production_units,0),2),0)) failures
UNION ALL
SELECT 'fg_wac_energy'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT product_id FROM manufacturing_v2.finished_goods_inventory WHERE energy_cogs_eur<>coalesce(round((opening_energy_value_eur+production_energy_value_eur)*shipped_units/nullif(opening_units+good_production_units,0),2),0)) failures
UNION ALL
SELECT 'fg_wac_overhead'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT product_id FROM manufacturing_v2.finished_goods_inventory WHERE overhead_cogs_eur<>coalesce(round((opening_overhead_value_eur+production_overhead_value_eur)*shipped_units/nullif(opening_units+good_production_units,0),2),0)) failures
UNION ALL
SELECT 'sales_fg_quantity_component_totals'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH s AS (SELECT month_id,product_id,sum(units_shipped) AS qty,sum(material_cogs_eur) AS material,sum(inbound_freight_cogs_eur) AS inbound_freight,sum(labor_cogs_eur) AS labor,sum(energy_cogs_eur) AS energy,sum(overhead_cogs_eur) AS overhead FROM manufacturing_v2.sales GROUP BY month_id,product_id) SELECT i.product_id FROM manufacturing_v2.finished_goods_inventory i LEFT JOIN s USING(month_id,product_id) WHERE i.shipped_units<>coalesce(s.qty,0) OR i.material_cogs_eur<>coalesce(s.material,0) OR i.inbound_freight_cogs_eur<>coalesce(s.inbound_freight,0) OR i.labor_cogs_eur<>coalesce(s.labor,0) OR i.energy_cogs_eur<>coalesce(s.energy,0) OR i.overhead_cogs_eur<>coalesce(s.overhead,0)) failures
UNION ALL
SELECT 'sales_component_cent_allocation'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH pool AS (
SELECT s.month_id,s.product_id,s.sales_line_id,s.units_shipped AS weight,v.component,v.cents,v.actual
FROM manufacturing_v2.sales s JOIN manufacturing_v2.finished_goods_inventory i USING(month_id,product_id)
CROSS JOIN LATERAL (VALUES ('material',i.material_cogs_eur*100,s.material_cogs_eur*100),('inbound_freight',i.inbound_freight_cogs_eur*100,s.inbound_freight_cogs_eur*100),('labor',i.labor_cogs_eur*100,s.labor_cogs_eur*100),('energy',i.energy_cogs_eur*100,s.energy_cogs_eur*100),('overhead',i.overhead_cogs_eur*100,s.overhead_cogs_eur*100)) v(component,cents,actual)
), totals AS (
SELECT month_id,product_id,sales_line_id,weight,component,cents,actual,sum(weight) OVER (PARTITION BY month_id,product_id,component) AS denominator FROM pool
), initial AS (
SELECT month_id,product_id,sales_line_id,weight,component,cents,actual,floor(cents*weight/denominator) AS base,
mod(cents*weight,denominator) AS remainder FROM totals
), ranked AS (
SELECT sales_line_id,weight,component,actual,base,cents-sum(base) OVER (PARTITION BY month_id,product_id,component) AS residual,
row_number() OVER (PARTITION BY month_id,product_id,component ORDER BY remainder DESC,sales_line_id) AS priority FROM initial
) SELECT sales_line_id,component FROM ranked WHERE actual<>base+CASE WHEN priority<=residual THEN 1 ELSE 0 END) failures
UNION ALL
SELECT 'sales_segment_discount'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT s.sales_line_id FROM manufacturing_v2.sales s JOIN manufacturing_v2.customers c USING(customer_id) WHERE NOT (CASE c.segment WHEN 'OEM' THEN s.discount_pct BETWEEN 5 AND 10 WHEN 'Tier 1' THEN s.discount_pct BETWEEN 3 AND 7 WHEN 'Aftermarket' THEN s.discount_pct BETWEEN 0 AND 3 ELSE false END)) failures
UNION ALL
SELECT 'outbound_rate_envelope'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH x AS (SELECT s.*,CASE c.segment WHEN 'OEM' THEN 1.20 WHEN 'Tier 1' THEN 1.50 ELSE 2.20 END AS base FROM manufacturing_v2.sales s JOIN manufacturing_v2.customers c USING(customer_id)) SELECT sales_line_id FROM x WHERE outbound_freight_rate_eur_per_unit < base*.95*.97-.00005 OR outbound_freight_rate_eur_per_unit > base*1.05*1.03+.00005) failures
UNION ALL
SELECT 'opex_resource_revenue_drivers'::text AS check_name, count(*)::bigint AS failed_rows FROM (WITH revenue AS (SELECT month_id,sum(net_revenue_eur) AS revenue FROM manufacturing_v2.sales GROUP BY month_id),calendar AS (SELECT month_id,row_number() OVER (ORDER BY month_id)-1 AS elapsed FROM manufacturing_v2.months)
SELECT o.month_id FROM manufacturing_v2.operating_expenses o JOIN calendar c USING(month_id) LEFT JOIN revenue r USING(month_id)
WHERE o.fixed_amount_eur<>round((CASE o.expense_category WHEN 'selling' THEN 26000 ELSE 38000 END)*(1+.0015*c.elapsed),2)
OR (o.expense_category='selling' AND (o.variable_rate_pct<>2 OR o.variable_driver_amount_eur<>coalesce(r.revenue,0)))) failures
UNION ALL
SELECT 'complete_opex_categories'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT m.month_id FROM manufacturing_v2.months m LEFT JOIN manufacturing_v2.operating_expenses o USING(month_id) GROUP BY m.month_id HAVING count(o.expense_category)<>2) failures
UNION ALL
SELECT 'monthly_pnl_no_fanout'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT 1 WHERE (SELECT sum(revenue) FROM manufacturing_v2.bi_monthly_pnl)<>(SELECT sum(net_revenue_eur) FROM manufacturing_v2.sales) OR (SELECT sum(cogs) FROM manufacturing_v2.bi_monthly_pnl)<>(SELECT sum(cogs_eur) FROM manufacturing_v2.sales) OR (SELECT sum(outbound_freight) FROM manufacturing_v2.bi_monthly_pnl)<>(SELECT sum(outbound_freight_eur) FROM manufacturing_v2.sales)) failures
UNION ALL
SELECT 'product_profit_no_fanout'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT 1 WHERE (SELECT sum(net_revenue_eur) FROM manufacturing_v2.bi_product_month_profitability)<>(SELECT sum(net_revenue_eur) FROM manufacturing_v2.sales) OR (SELECT sum(cogs_eur) FROM manufacturing_v2.bi_product_month_profitability)<>(SELECT sum(cogs_eur) FROM manufacturing_v2.sales)) failures
UNION ALL
SELECT 'phase7_pnl_baseline'::text AS check_name, count(*)::bigint AS failed_rows FROM (SELECT period,metric FROM manufacturing_v2.audit_pnl_reconciliation WHERE NOT passed OR passed IS NULL) failures;

SELECT check_name,failed_rows FROM manufacturing_v2.audit_validation_results ORDER BY check_name;
SELECT period,metric,expected,actual,difference,passed FROM manufacturing_v2.audit_pnl_reconciliation ORDER BY period,metric;
DO $validation$
DECLARE failures text;
BEGIN
 SELECT string_agg(check_name || '=' || failed_rows, ', ') INTO failures
 FROM manufacturing_v2.audit_validation_results WHERE failed_rows<>0;
 IF failures IS NOT NULL THEN RAISE EXCEPTION 'Migration validation failed: %', failures; END IF;
END;
$validation$;
