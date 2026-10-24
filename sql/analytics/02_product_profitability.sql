-- Product profitability
-- Business question: Which products create profit and how do realized prices compare with COGS per unit?
-- Sources: bi_product_profitability; bi_product_month_profitability
-- Output grain: Q1 product/full period; Q2 product/year
-- KPI definitions: GP=revenue−five-component COGS; contribution=GP−outbound; realized price=revenue/shipped units.
-- Logic: DENSE_RANK and cumulative contribution ordered by gross profit; annual ratio-of-sums with same-product LAG.
-- Limitations: Product contribution excludes unallocated company opex and idle losses. Price/cost changes are descriptive, not causal price-volume-mix attribution.
-- Read-only SELECT statements; run through run_analytics.py or psql in BEGIN READ ONLY.

SELECT *
     , dense_rank() OVER (ORDER BY gross_profit_eur DESC) AS gross_profit_rank
     , dense_rank() OVER (ORDER BY gross_margin_pct DESC NULLS LAST) AS margin_rank
     , 100 * net_revenue_eur / NULLIF(sum(net_revenue_eur) OVER ()
                                    , 0) AS revenue_share_pct
     , 100 * sum(gross_profit_eur) OVER (ORDER BY gross_profit_eur DESC
                                                , product_id
                                         ROWS UNBOUNDED PRECEDING) / NULLIF(sum(gross_profit_eur) OVER ()
                                                                          , 0) AS cumulative_gp_share_pct
FROM manufacturing_v2.bi_product_profitability
ORDER BY gross_profit_rank
       , product_id;

WITH a AS (
       SELECT product_id
            , product_name
            , CAST(EXTRACT(YEAR FROM month_id) AS integer) AS year
            , sum(units_shipped) AS units
            , sum(net_revenue_eur) AS revenue_eur
            , sum(cogs_eur) AS cogs_eur
            , sum(gross_profit_eur) AS gross_profit_eur
       FROM manufacturing_v2.bi_product_month_profitability
       GROUP BY 1, 2, 3
     )
   , u AS (
       SELECT *
            , revenue_eur / NULLIF(units, 0) AS realized_price_eur
            , cogs_eur / NULLIF(units, 0) AS cogs_per_unit_eur
            , 100 * gross_profit_eur / NULLIF(revenue_eur, 0) AS gross_margin_pct
       FROM a
     )
  SELECT *
       , realized_price_eur - lag(realized_price_eur) OVER (PARTITION BY product_id
                                                            ORDER BY year) AS price_change_eur
       , cogs_per_unit_eur - lag(cogs_per_unit_eur) OVER (PARTITION BY product_id
                                                          ORDER BY year) AS unit_cogs_change_eur
  FROM u
  ORDER BY product_id
         , year
