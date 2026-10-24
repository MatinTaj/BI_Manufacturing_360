-- Logistics and distribution
-- Business question: How do outbound distribution costs differ by segment and how is inbound freight recognized?
-- Sources: bi_sales_detail; bi_procurement_receipts; sales
-- Output grain: Q1 year/customer segment; Q2 year freight recognition bridge
-- KPI definitions: Outbound EUR/unit=freight/shipped; distribution burden=outbound/revenue; inbound receipt amounts are capitalized, not immediately expensed.
-- Logic: Segment ratios of sums; independent annual receipt and sales aggregates joined to calendar-year spine.
-- Limitations: Inbound purchases and recognized inbound COGS differ through inventory. Outbound is below GP, never inventory. Rates are synthetic blended per-unit costs; geography and minimum shipment charges are absent.
-- Read-only SELECT statements; run through run_analytics.py or psql in BEGIN READ ONLY.

SELECT CAST(EXTRACT(YEAR FROM month_id) AS integer) AS year
     , segment
     , sum(units_shipped) AS shipped_units
     , sum(net_revenue_eur) AS revenue_eur
     , sum(outbound_freight_eur) AS outbound_eur
     , sum(outbound_freight_eur) / NULLIF(sum(units_shipped)
                                        , 0) AS outbound_eur_per_unit
     , 100 * sum(outbound_freight_eur) / NULLIF(sum(net_revenue_eur)
                                              , 0) AS outbound_to_revenue_pct
     , sum(gross_profit_eur) AS gross_profit_eur
     , sum(contribution_after_outbound_eur) AS contribution_eur
FROM manufacturing_v2.bi_sales_detail
GROUP BY 1, 2
ORDER BY year
       , segment;

WITH r AS (
       SELECT CAST(EXTRACT(YEAR FROM receipt_date) AS integer) AS year
            , sum(inbound_freight_eur) AS inbound_receipts_eur
       FROM manufacturing_v2.bi_procurement_receipts
       GROUP BY 1
     )
   , s AS (
       SELECT CAST(EXTRACT(YEAR FROM month_id) AS integer) AS year
            , sum(inbound_freight_cogs_eur) AS inbound_cogs_eur
            , sum(outbound_freight_eur) AS outbound_expense_eur
       FROM manufacturing_v2.sales
       GROUP BY 1
     )
   , i AS (
       SELECT m.year
            , sum(r.closing_inbound_freight_value_eur - r.opening_inbound_freight_value_eur) AS raw_freight_inventory_change_eur
       FROM manufacturing_v2.raw_material_inventory AS r
            INNER JOIN manufacturing_v2.months AS m USING (month_id)
       GROUP BY 1
     )
   , f AS (
       SELECT m.year
            , sum(f.closing_inbound_freight_value_eur - f.opening_inbound_freight_value_eur) AS fg_freight_inventory_change_eur
       FROM manufacturing_v2.finished_goods_inventory AS f
            INNER JOIN manufacturing_v2.months AS m USING (month_id)
       GROUP BY 1
     )
   , l AS (
       SELECT CAST(EXTRACT(YEAR FROM month_id) AS integer) AS year
            , sum(inbound_freight_production_loss_expense_eur) AS inbound_loss_eur
       FROM manufacturing_v2.production_cost_allocation
       GROUP BY 1
     )
  SELECT s.year
       , r.inbound_receipts_eur
       , s.inbound_cogs_eur
       , s.outbound_expense_eur
       , i.raw_freight_inventory_change_eur
       , f.fg_freight_inventory_change_eur
       , l.inbound_loss_eur
       , r.inbound_receipts_eur - s.inbound_cogs_eur - i.raw_freight_inventory_change_eur - f.fg_freight_inventory_change_eur - l.inbound_loss_eur AS inbound_bridge_difference_eur
  FROM s
       INNER JOIN r USING (year)
       INNER JOIN i USING (year)
       INNER JOIN f USING (year)
       INNER JOIN l USING (year)
  ORDER BY year
