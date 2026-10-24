-- Supplier performance and procurement
-- Business question: How concentrated is purchasing, and do observed receipts support supplier comparisons?
-- Sources: suppliers LEFT JOIN bi_procurement_receipts; material receipt details
-- Output grain: Q1 supplier/full period; Q2 material/receipt year
-- KPI definitions: OTD=on-time receipt count/all observed receipts; lead days=receipt−order; purchase price=purchase EUR/kg.
-- Logic: Retains suppliers without receipts; COUNT(receipt_id) avoids counting null extended rows; weighted spend/quantity rates.
-- Limitations: Suppliers with zero receipts have NULL performance, not zero OTD. Synthetic scheduled/full receipts limit real supplier reliability conclusions. Receipt-based OTD is not order-line fill rate.
-- Read-only SELECT statements; run through run_analytics.py or psql in BEGIN READ ONLY.

WITH a AS (
       SELECT s.supplier_id
            , s.supplier_name
            , s.on_time_delivery_target
            , count(r.receipt_id) AS receipts
            , count(r.receipt_id) FILTER (WHERE r.on_time) AS on_time_receipts
            , sum(r.purchase_value_eur) AS purchase_eur
            , sum(r.inbound_freight_eur) AS inbound_freight_eur
            , sum(r.received_kg) AS received_kg
            , avg(r.actual_lead_time_days) AS mean_lead_days
            , avg(GREATEST(r.receipt_date - r.expected_receipt_date
                         , 0)) FILTER (WHERE r.receipt_id IS NOT NULL) AS mean_late_days
       FROM manufacturing_v2.suppliers AS s
            LEFT JOIN manufacturing_v2.bi_procurement_receipts AS r USING (supplier_id)
       GROUP BY 1, 2, 3
     )
  SELECT *
       , 100.0 * on_time_receipts / NULLIF(receipts, 0) AS on_time_pct
       , 100.0 * on_time_receipts / NULLIF(receipts, 0) - 100 * on_time_delivery_target AS target_gap_pp
       , 100 * COALESCE(purchase_eur, 0) / NULLIF(sum(purchase_eur) OVER ()
                                                , 0) AS purchase_share_pct
  FROM a
  ORDER BY purchase_eur DESC NULLS LAST
         , supplier_id;

WITH a AS (
       SELECT material_id
            , material_name
            , CAST(EXTRACT(YEAR FROM receipt_date) AS integer) AS year
            , count(*) AS receipts
            , sum(received_kg) AS received_kg
            , sum(purchase_value_eur) AS purchase_eur
            , sum(inbound_freight_eur) AS inbound_eur
            , sum(landed_receipt_value_eur) AS landed_eur
       FROM manufacturing_v2.bi_procurement_receipts
       GROUP BY 1, 2, 3
     )
   , c AS (
       SELECT *
            , purchase_eur / NULLIF(received_kg, 0) AS weighted_purchase_price_eur_per_kg
            , landed_eur / NULLIF(received_kg, 0) AS landed_eur_per_kg
       FROM a
     )
  SELECT *
       , 100 * (weighted_purchase_price_eur_per_kg - lag(weighted_purchase_price_eur_per_kg) OVER (PARTITION BY material_id
                                                                                                   ORDER BY year)) / NULLIF(lag(weighted_purchase_price_eur_per_kg) OVER (PARTITION BY material_id
                                                                                                                                                                          ORDER BY year)
                                                                                                                          , 0) AS purchase_price_yoy_pct
  FROM c
  ORDER BY material_id
         , year
