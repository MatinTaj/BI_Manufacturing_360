-- Analytical direct/support labor decomposition; SELECT only, no new booked component.
-- Existing labor COGS remains authoritative. Direct wins exact remainder ties;
-- sale-line ties use sales_line_id. Initial finished-goods labor must be zero.
WITH RECURSIVE inputs AS (
 SELECT f.month_id,f.product_id,
        row_number() OVER(PARTITION BY f.product_id ORDER BY f.month_id) AS rn,
        f.opening_labor_value_eur*100 AS opening_total_cents,
        f.production_labor_value_eur*100 AS addition_total_cents,
        f.labor_cogs_eur*100 AS cogs_total_cents,
        f.closing_labor_value_eur*100 AS closing_total_cents,
        CASE WHEN a.good_units>0 THEN a.production_labor_cost_eur*100 ELSE 0::numeric END AS direct_addition_cents,
        f.production_labor_value_eur=a.capitalized_labor_cost_eur AS addition_matches
 FROM manufacturing_v2.finished_goods_inventory f
 JOIN manufacturing_v2.production_cost_allocation a USING(month_id,product_id)
), ledger AS (
 SELECT i.*,0::numeric AS opening_direct_cents,split.direct_cogs_cents,
        (i.direct_addition_cents-split.direct_cogs_cents)::numeric AS closing_direct_cents,
        (i.opening_total_cents=0 AND i.addition_matches AND v.direct_cents BETWEEN 0 AND v.total_cents
         AND v.issue_cents BETWEEN 0 AND v.total_cents
         AND i.opening_total_cents+i.addition_total_cents-i.cogs_total_cents=i.closing_total_cents) AS valid
 FROM inputs i
 CROSS JOIN LATERAL (VALUES(i.direct_addition_cents,i.opening_total_cents+i.addition_total_cents,i.cogs_total_cents)) v(direct_cents,total_cents,issue_cents)
 CROSS JOIN LATERAL (SELECT (CASE WHEN v.total_cents=0 THEN 0::numeric ELSE
 div(v.direct_cents*v.issue_cents,v.total_cents)
 + CASE WHEN v.issue_cents-div(v.direct_cents*v.issue_cents,v.total_cents)-div((v.total_cents-v.direct_cents)*v.issue_cents,v.total_cents)>0
             AND mod(v.direct_cents*v.issue_cents,v.total_cents)>=mod((v.total_cents-v.direct_cents)*v.issue_cents,v.total_cents)
        THEN 1 ELSE 0 END END)::numeric AS direct_cogs_cents) split
 WHERE i.rn=1
 UNION ALL
 SELECT i.*,l.closing_direct_cents AS opening_direct_cents,split.direct_cogs_cents,
        (l.closing_direct_cents+i.direct_addition_cents-split.direct_cogs_cents)::numeric AS closing_direct_cents,
        (l.valid AND i.opening_total_cents=l.closing_total_cents AND i.addition_matches
         AND i.month_id=(l.month_id+interval '1 month')::date
         AND v.direct_cents BETWEEN 0 AND v.total_cents AND v.issue_cents BETWEEN 0 AND v.total_cents
         AND i.opening_total_cents+i.addition_total_cents-i.cogs_total_cents=i.closing_total_cents) AS valid
 FROM ledger l JOIN inputs i ON i.product_id=l.product_id AND i.rn=l.rn+1
 CROSS JOIN LATERAL (VALUES(l.closing_direct_cents+i.direct_addition_cents,i.opening_total_cents+i.addition_total_cents,i.cogs_total_cents)) v(direct_cents,total_cents,issue_cents)
 CROSS JOIN LATERAL (SELECT (CASE WHEN v.total_cents=0 THEN 0::numeric ELSE
 div(v.direct_cents*v.issue_cents,v.total_cents)
 + CASE WHEN v.issue_cents-div(v.direct_cents*v.issue_cents,v.total_cents)-div((v.total_cents-v.direct_cents)*v.issue_cents,v.total_cents)>0
             AND mod(v.direct_cents*v.issue_cents,v.total_cents)>=mod((v.total_cents-v.direct_cents)*v.issue_cents,v.total_cents)
        THEN 1 ELSE 0 END END)::numeric AS direct_cogs_cents) split
), line_weights AS (
 SELECT s.sales_line_id,s.month_id,s.product_id,s.labor_cogs_eur*100 AS line_labor_cents,
        l.direct_cogs_cents,l.cogs_total_cents,l.valid,
        CASE WHEN l.cogs_total_cents=0 THEN 0::numeric ELSE div(l.direct_cogs_cents*s.labor_cogs_eur*100,l.cogs_total_cents) END AS base_cents,
        CASE WHEN l.cogs_total_cents=0 THEN 0::numeric ELSE mod(l.direct_cogs_cents*s.labor_cogs_eur*100,l.cogs_total_cents) END AS remainder
 FROM manufacturing_v2.sales s JOIN ledger l USING(month_id,product_id)
), ranked AS (
 SELECT *,row_number() OVER(PARTITION BY month_id,product_id ORDER BY remainder DESC,sales_line_id) AS remainder_rank,
        sum(base_cents) OVER(PARTITION BY month_id,product_id) AS allocated_base_cents
 FROM line_weights
), allocated AS (
 SELECT *,base_cents+CASE WHEN remainder_rank<=direct_cogs_cents-allocated_base_cents THEN 1 ELSE 0 END AS line_direct_cents
 FROM ranked
), final_exposure AS (
 SELECT sales_line_id,line_direct_cents/100 AS direct_labor_cogs_exposure_eur,
        (line_labor_cents-line_direct_cents)/100 AS support_labor_cogs_exposure_eur,
        (valid AND line_direct_cents BETWEEN 0 AND line_labor_cents
         AND sum(line_direct_cents) OVER(PARTITION BY month_id,product_id)=direct_cogs_cents
         AND sum(line_labor_cents) OVER(PARTITION BY month_id,product_id)=cogs_total_cents) AS direct_labor_exposure_valid
 FROM allocated
)
SELECT s.line_id, s.segment, s.category, s.cogs_eur, s.month_id, s.product_id, s.customer_id, s.discount_pct, s.product_name, s.customer_name, s.sales_line_id, s.shipment_date, s.units_shipped, s.labor_cogs_eur, s.energy_cogs_eur, s.net_revenue_eur, s.requested_units, s.gross_margin_pct, s.gross_profit_eur, s.gross_revenue_eur, s.material_cogs_eur, s.overhead_cogs_eur, s.unfulfilled_units, s.net_unit_price_eur, s.discount_amount_eur, s.list_unit_price_eur, s.outbound_freight_eur, s.inbound_freight_cogs_eur, s.weighted_average_unit_cost_eur, s.contribution_after_outbound_eur, s.outbound_freight_rate_eur_per_unit, e.direct_labor_cogs_exposure_eur,e.support_labor_cogs_exposure_eur,e.direct_labor_exposure_valid FROM manufacturing_v2.bi_sales_detail s JOIN final_exposure e USING(sales_line_id);
