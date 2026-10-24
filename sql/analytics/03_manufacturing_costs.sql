-- Manufacturing costs and activity drivers
-- Business question: Which cost components dominate, and what drives line conversion economics?
-- Sources: production_cost_allocation; bi_line_manufacturing_costs
-- Output grain: Q1 year/component; Q2 line/year
-- KPI definitions: Manufacturing total=five components; labor rate=cost/hours; energy tariff=cost/kWh; activity intensity=activity/attempted units.
-- Logic: LATERAL VALUES unpivots only five authoritative components; line pools analyzed independently from allocations.
-- Limitations: Never add cost pools to product allocations, or landed material subtotal to purchase/freight. Manufacturing additions differ from sales COGS because inventory defers costs.
-- Read-only SELECT statements; run through run_analytics.py or psql in BEGIN READ ONLY.

WITH c AS (
       SELECT CAST(EXTRACT(YEAR FROM a.month_id) AS integer) AS year
            , v.component
            , sum(v.amount) AS cost_eur
       FROM manufacturing_v2.production_cost_allocation AS a
            CROSS JOIN LATERAL ((VALUES ('purchase_material', a.purchase_material_cost_eur)
                                      , ('inbound_freight', a.inbound_freight_cost_eur)
                                      , ('labor', a.labor_cost_eur)
                                      , ('energy', a.energy_cost_eur)
                                      , ('overhead', a.manufacturing_overhead_eur))) AS v (component, amount)
       GROUP BY 1, 2
     )
  SELECT *
       , 100 * cost_eur / NULLIF(sum(cost_eur) OVER (PARTITION BY year)
                               , 0) AS manufacturing_share_pct
  FROM c
  ORDER BY year
         , cost_eur DESC;

SELECT line_id
     , line_name
     , CAST(EXTRACT(YEAR FROM month_id) AS integer) AS year
     , sum(attempted_units) AS attempted_units
     , sum(labor_hours) AS total_labor_hours
     , sum(production_labor_hours) AS activity_labor_hours
     , sum(support_labor_hours) AS support_hours
     , sum(energy_kwh) AS total_kwh
     , sum(activity_energy_kwh) AS activity_kwh
     , sum(base_energy_kwh) AS standby_kwh
     , sum(total_conversion_cost_eur) AS conversion_eur
     , sum(idle_cost_eur) AS idle_eur
     , sum(labor_cost_eur) / NULLIF(sum(labor_hours)
                                  , 0) AS realized_labor_rate_eur_per_hour
     , sum(energy_cost_eur) / NULLIF(sum(energy_kwh)
                                   , 0) AS realized_tariff_eur_per_kwh
     , sum(production_labor_hours) / NULLIF(sum(attempted_units)
                                          , 0) AS labor_hours_per_attempt
     , sum(activity_energy_kwh) / NULLIF(sum(attempted_units)
                                       , 0) AS kwh_per_attempt
FROM manufacturing_v2.bi_line_manufacturing_costs
GROUP BY 1, 2, 3
ORDER BY 1
       , 3
