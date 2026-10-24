-- Production efficiency and defects
-- Business question: Which lines have capacity pressure and where are defects concentrated?
-- Sources: bi_line_production_performance; bi_production_performance
-- Output grain: Q1 line/year; Q2 product/full period
-- KPI definitions: Utilization=attempted/effective capacity; defect rate=defective/attempted; yield=good/attempted.
-- Logic: Ratios of annual sums, annual LAG changes and defect-count ranking; no sales joins.
-- Limitations: Capacity utilization is not OEE. No machine-speed or quality inspection detail; defect volume depends on production mix. No scrap-sale recovery assumption.
-- Read-only SELECT statements; run through run_analytics.py or psql in BEGIN READ ONLY.

WITH a AS (
       SELECT line_id
            , line_name
            , CAST(EXTRACT(YEAR FROM month_id) AS integer) AS year
            , sum(attempted_units) AS attempted_units
            , sum(good_units) AS good_units
            , sum(defective_units) AS defective_units
            , sum(nominal_capacity_units) AS nominal_capacity
            , sum(effective_capacity_units) AS effective_capacity
       FROM manufacturing_v2.bi_line_production_performance
       GROUP BY 1, 2, 3
     )
   , k AS (
       SELECT *
            , 100.0 * attempted_units / NULLIF(effective_capacity, 0) AS utilization_pct
            , 100.0 * defective_units / NULLIF(attempted_units, 0) AS defect_rate_pct
       FROM a
     )
  SELECT *
       , utilization_pct - lag(utilization_pct) OVER (PARTITION BY line_id
                                                      ORDER BY year) AS utilization_change_pp
       , defect_rate_pct - lag(defect_rate_pct) OVER (PARTITION BY line_id
                                                      ORDER BY year) AS defect_change_pp
  FROM k
  ORDER BY line_id
         , year;

SELECT product_id
     , product_name
     , line_id
     , sum(attempted_units) AS attempted_units
     , sum(defective_units) AS defective_units
     , sum(good_units) AS good_units
     , 100 * CAST(sum(defective_units) AS numeric) / NULLIF(sum(attempted_units)
                                                          , 0) AS defect_rate_pct
     , 100 * CAST(sum(good_units) AS numeric) / NULLIF(sum(attempted_units)
                                                     , 0) AS yield_pct
     , dense_rank() OVER (ORDER BY sum(defective_units) DESC) AS defect_volume_rank
FROM manufacturing_v2.bi_production_performance
GROUP BY 1, 2, 3
ORDER BY defect_volume_rank
       , product_id
