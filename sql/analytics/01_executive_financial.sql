-- Executive financial performance
-- Business question: How did revenue and operating profit change, and which months drove the result?
-- Sources: bi_monthly_pnl; bi_period_pnl
-- Output grain: Q1 year; Q2 month
-- KPI definitions: Gross margin=GP/revenue; operating margin=OP/revenue; YoY=(current/prior−1); percentage changes use percentage points.
-- Logic: LAG over annual results and same calendar month; cumulative SUM resets each year.
-- Limitations: Initial-year YoY is NULL. OP follows approved policy; net income and cash flow are outside scope.
-- Read-only SELECT statements; run through run_analytics.py or psql in BEGIN READ ONLY.

WITH a AS (
       SELECT *
            , lag(revenue) OVER (ORDER BY period) AS prior_revenue
            , lag(operating_profit) OVER (ORDER BY period) AS prior_operating_profit
            , lag(operating_margin_pct) OVER (ORDER BY period) AS prior_margin
       FROM manufacturing_v2.bi_period_pnl
       WHERE period <> 'combined'
     )
  SELECT *
       , 100 * (revenue - prior_revenue) / NULLIF(prior_revenue, 0) AS revenue_yoy_pct
       , 100 * (operating_profit - prior_operating_profit) / NULLIF(prior_operating_profit, 0) AS operating_profit_yoy_pct
       , operating_margin_pct - prior_margin AS operating_margin_change_pp
  FROM a
  ORDER BY period;

WITH m AS (
       SELECT *
            , lag(revenue) OVER (PARTITION BY EXTRACT(MONTH FROM month_id)
                                 ORDER BY month_id) AS same_month_prior_revenue
       FROM manufacturing_v2.bi_monthly_pnl
     )
  SELECT *
       , 100 * (revenue - same_month_prior_revenue) / NULLIF(same_month_prior_revenue, 0) AS revenue_yoy_pct
       , sum(revenue) OVER (PARTITION BY year
                            ORDER BY month_id
                            ROWS UNBOUNDED PRECEDING) AS ytd_revenue_eur
       , sum(operating_profit) OVER (PARTITION BY year
                                     ORDER BY month_id
                                     ROWS UNBOUNDED PRECEDING) AS ytd_operating_profit_eur
  FROM m
  ORDER BY month_id
