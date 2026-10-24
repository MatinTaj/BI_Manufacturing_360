-- Customer concentration
-- Business question: How dependent is revenue on the largest customers, and does their contribution justify concentration?
-- Sources: bi_customer_month_performance
-- Output grain: Q1 customer/year; Q2 year
-- KPI definitions: Revenue share=customer/year revenue divided by company/year; HHI=sum of squared percentage shares; contribution=GP−outbound.
-- Logic: Annual customer aggregation, deterministic ROW_NUMBER ties by customer_id, cumulative revenue windows and conditional top-N sums.
-- Limitations: HHI describes this fictional customer book, not an antitrust market measure. No contract renewal, credit risk or group ownership data; customer contribution excludes shared opex.
-- Read-only SELECT statements; run through run_analytics.py or psql in BEGIN READ ONLY.

WITH a AS (
       SELECT CAST(EXTRACT(YEAR FROM month_id) AS integer) AS year
            , customer_id
            , customer_name
            , segment
            , sum(net_revenue_eur) AS revenue_eur
            , sum(gross_profit_eur) AS gross_profit_eur
            , sum(contribution_after_outbound_eur) AS contribution_eur
       FROM manufacturing_v2.bi_customer_month_performance
       GROUP BY 1, 2, 3, 4
     )
  SELECT *
       , row_number() OVER (PARTITION BY year
                            ORDER BY revenue_eur DESC
                                   , customer_id) AS revenue_rank
       , 100 * revenue_eur / NULLIF(sum(revenue_eur) OVER (PARTITION BY year)
                                  , 0) AS revenue_share_pct
       , 100 * sum(revenue_eur) OVER (PARTITION BY year
                                      ORDER BY revenue_eur DESC
                                             , customer_id
                                      ROWS UNBOUNDED PRECEDING) / NULLIF(sum(revenue_eur) OVER (PARTITION BY year)
                                                                       , 0) AS cumulative_share_pct
       , 100 * contribution_eur / NULLIF(revenue_eur, 0) AS contribution_margin_pct
  FROM a
  ORDER BY year
         , revenue_rank;

WITH a AS (
       SELECT CAST(EXTRACT(YEAR FROM month_id) AS integer) AS year
            , customer_id
            , sum(net_revenue_eur) AS revenue
       FROM manufacturing_v2.bi_customer_month_performance
       GROUP BY 1, 2
     )
   , r AS (
       SELECT *
            , row_number() OVER (PARTITION BY year
                                 ORDER BY revenue DESC
                                        , customer_id) AS rn
            , 100 * revenue / NULLIF(sum(revenue) OVER (PARTITION BY year)
                                   , 0) AS share_pct
       FROM a
     )
  SELECT year
       , count(*) AS active_customers
       , 100 * sum(revenue) FILTER (WHERE rn <= 1) / NULLIF(sum(revenue)
                                                          , 0) AS top1_share_pct
       , 100 * sum(revenue) FILTER (WHERE rn <= 5) / NULLIF(sum(revenue)
                                                          , 0) AS top5_share_pct
       , 100 * sum(revenue) FILTER (WHERE rn <= 10) / NULLIF(sum(revenue)
                                                           , 0) AS top10_share_pct
       , sum(share_pct * share_pct) AS customer_hhi
  FROM r
  GROUP BY year
  ORDER BY year
