-- Inventory valuation and turnover
-- Business question: How much cost is tied up in inventory and how quickly does it turn?
-- Sources: raw_material_inventory; finished_goods_inventory; months; bi_monthly_pnl
-- Output grain: Q1 year; Q2 month
-- KPI definitions: FG turns=annual COGS/mean monthly midpoint FG; raw turns=annual landed issues/mean raw midpoint; combined days=calendar days*mean combined inventory/COGS.
-- Logic: Aggregate each inventory fact to month before joining; average (opening+closing)/2 across months; calendar carries actual 365/366 days.
-- Limitations: Midpoints approximate time-average balances; zero opening FG in 2024 creates startup bias. No WIP, daily balances or receivables/payables: this is not a cash conversion cycle. Closing balances are not summed across months.
-- Read-only SELECT statements; run through run_analytics.py or psql in BEGIN READ ONLY.

WITH r AS (
       SELECT month_id
            , sum(opening_value_eur) AS opening_raw
            , sum(closing_value_eur) AS closing_raw
            , sum(issued_material_value_eur) AS raw_issues
       FROM manufacturing_v2.raw_material_inventory
       GROUP BY 1
     )
   , f AS (
       SELECT month_id
            , sum(opening_value_eur) AS opening_fg
            , sum(closing_value_eur) AS closing_fg
            , sum(cogs_eur) AS cogs
       FROM manufacturing_v2.finished_goods_inventory
       GROUP BY 1
     )
   , a AS (
       SELECT m.year
            , sum(m.days_in_month) AS days
            , sum(f.cogs) AS cogs_eur
            , sum(r.raw_issues) AS landed_raw_issues_eur
            , avg((r.opening_raw + r.closing_raw) / 2) AS avg_raw_eur
            , avg((f.opening_fg + f.closing_fg) / 2) AS avg_fg_eur
       FROM manufacturing_v2.months AS m
            INNER JOIN r USING (month_id)
            INNER JOIN f USING (month_id)
       GROUP BY m.year
     )
  SELECT *
       , cogs_eur / NULLIF(avg_fg_eur, 0) AS fg_turns
       , landed_raw_issues_eur / NULLIF(avg_raw_eur, 0) AS raw_turns
       , cogs_eur / NULLIF(avg_raw_eur + avg_fg_eur
                         , 0) AS combined_turns
       , days * (avg_raw_eur + avg_fg_eur) / NULLIF(cogs_eur, 0) AS inventory_days_proxy
  FROM a
  ORDER BY year;

WITH r AS (
       SELECT month_id
            , sum(closing_value_eur) AS closing_raw_eur
       FROM manufacturing_v2.raw_material_inventory
       GROUP BY 1
     )
   , f AS (
       SELECT month_id
            , sum(closing_value_eur) AS closing_fg_eur
       FROM manufacturing_v2.finished_goods_inventory
       GROUP BY 1
     )
  SELECT month_id
       , closing_raw_eur
       , closing_fg_eur
       , closing_raw_eur + closing_fg_eur AS total_closing_inventory_eur
       , closing_raw_eur + closing_fg_eur - lag(closing_raw_eur + closing_fg_eur) OVER (ORDER BY month_id) AS inventory_change_eur
  FROM r
       INNER JOIN f USING (month_id)
  ORDER BY month_id
