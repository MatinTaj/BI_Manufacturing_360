-- Quality gates and negative-control fixtures; every failed_rows must be zero.
-- Q2: approved baseline comparisons. Q3: diagnostic unsafe fanout, counts only.

(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((SELECT CAST('duplicate_months' AS text) AS check_name
                                                                                      , CAST(count(*) AS bigint) AS failed_rows
                                                                                 FROM (SELECT month_id
                                                                                       FROM manufacturing_v2.months
                                                                                       GROUP BY month_id
                                                                                       HAVING count(*) > 1) AS failures

                                                                                 UNION ALL

                                                                                 SELECT CAST('null_months' AS text) AS check_name
                                                                                      , CAST(count(*) AS bigint) AS failed_rows
                                                                                 FROM (SELECT 1
                                                                                       FROM manufacturing_v2.months AS t
                                                                                       WHERE t.month_id IS NULL
                                                                                          OR t.year IS NULL
                                                                                          OR t.quarter IS NULL
                                                                                          OR t.month_number IS NULL
                                                                                          OR t.days_in_month IS NULL) AS failures)

                                                                                UNION ALL

                                                                                SELECT CAST('duplicate_production_lines' AS text) AS check_name
                                                                                     , CAST(count(*) AS bigint) AS failed_rows
                                                                                FROM (SELECT line_id
                                                                                      FROM manufacturing_v2.production_lines
                                                                                      GROUP BY line_id
                                                                                      HAVING count(*) > 1) AS failures)

                                                                               UNION ALL

                                                                               SELECT CAST('null_production_lines' AS text) AS check_name
                                                                                    , CAST(count(*) AS bigint) AS failed_rows
                                                                               FROM (SELECT 1
                                                                                     FROM manufacturing_v2.production_lines AS t
                                                                                     WHERE t.line_id IS NULL
                                                                                        OR t.line_name IS NULL
                                                                                        OR t.monthly_capacity_units IS NULL
                                                                                        OR t.support_labor_hours_per_month IS NULL
                                                                                        OR t.base_energy_kwh_per_month IS NULL) AS failures)

                                                                              UNION ALL

                                                                              SELECT CAST('duplicate_materials' AS text) AS check_name
                                                                                   , CAST(count(*) AS bigint) AS failed_rows
                                                                              FROM (SELECT material_id
                                                                                    FROM manufacturing_v2.materials
                                                                                    GROUP BY material_id
                                                                                    HAVING count(*) > 1) AS failures)

                                                                             UNION ALL

                                                                             SELECT CAST('null_materials' AS text) AS check_name
                                                                                  , CAST(count(*) AS bigint) AS failed_rows
                                                                             FROM (SELECT 1
                                                                                   FROM manufacturing_v2.materials AS t
                                                                                   WHERE t.material_id IS NULL
                                                                                      OR t.material_name IS NULL
                                                                                      OR t.unit IS NULL
                                                                                      OR t.base_unit_cost_eur IS NULL) AS failures)

                                                                            UNION ALL

                                                                            SELECT CAST('duplicate_suppliers' AS text) AS check_name
                                                                                 , CAST(count(*) AS bigint) AS failed_rows
                                                                            FROM (SELECT supplier_id
                                                                                  FROM manufacturing_v2.suppliers
                                                                                  GROUP BY supplier_id
                                                                                  HAVING count(*) > 1) AS failures)

                                                                           UNION ALL

                                                                           SELECT CAST('null_suppliers' AS text) AS check_name
                                                                                , CAST(count(*) AS bigint) AS failed_rows
                                                                           FROM (SELECT 1
                                                                                 FROM manufacturing_v2.suppliers AS t
                                                                                 WHERE t.supplier_id IS NULL
                                                                                    OR t.supplier_name IS NULL
                                                                                    OR t.lead_time_days IS NULL
                                                                                    OR t.on_time_delivery_target IS NULL) AS failures)

                                                                          UNION ALL

                                                                          SELECT CAST('duplicate_customers' AS text) AS check_name
                                                                               , CAST(count(*) AS bigint) AS failed_rows
                                                                          FROM (SELECT customer_id
                                                                                FROM manufacturing_v2.customers
                                                                                GROUP BY customer_id
                                                                                HAVING count(*) > 1) AS failures)

                                                                         UNION ALL

                                                                         SELECT CAST('null_customers' AS text) AS check_name
                                                                              , CAST(count(*) AS bigint) AS failed_rows
                                                                         FROM (SELECT 1
                                                                               FROM manufacturing_v2.customers AS t
                                                                               WHERE t.customer_id IS NULL
                                                                                  OR t.customer_name IS NULL
                                                                                  OR t.segment IS NULL) AS failures)

                                                                        UNION ALL

                                                                        SELECT CAST('duplicate_products' AS text) AS check_name
                                                                             , CAST(count(*) AS bigint) AS failed_rows
                                                                        FROM (SELECT product_id
                                                                              FROM manufacturing_v2.products
                                                                              GROUP BY product_id
                                                                              HAVING count(*) > 1) AS failures)

                                                                       UNION ALL

                                                                       SELECT CAST('null_products' AS text) AS check_name
                                                                            , CAST(count(*) AS bigint) AS failed_rows
                                                                       FROM (SELECT 1
                                                                             FROM manufacturing_v2.products AS t
                                                                             WHERE t.product_id IS NULL
                                                                                OR t.product_name IS NULL
                                                                                OR t.category IS NULL
                                                                                OR t.line_id IS NULL
                                                                                OR t.base_selling_price_eur IS NULL
                                                                                OR t.standard_labor_hours_per_attempt IS NULL
                                                                                OR t.standard_energy_kwh_per_attempt IS NULL) AS failures)

                                                                      UNION ALL

                                                                      SELECT CAST('relationship_products_0' AS text) AS check_name
                                                                           , CAST(count(*) AS bigint) AS failed_rows
                                                                      FROM (SELECT 1
                                                                            FROM manufacturing_v2.products AS c
                                                                                 LEFT JOIN manufacturing_v2.production_lines AS p ON c.line_id = p.line_id
                                                                            WHERE p.line_id IS NULL) AS failures)

                                                                     UNION ALL

                                                                     SELECT CAST('duplicate_material_suppliers' AS text) AS check_name
                                                                          , CAST(count(*) AS bigint) AS failed_rows
                                                                     FROM (SELECT material_id
                                                                                , supplier_id
                                                                           FROM manufacturing_v2.material_suppliers
                                                                           GROUP BY material_id, supplier_id
                                                                           HAVING count(*) > 1) AS failures)

                                                                    UNION ALL

                                                                    SELECT CAST('null_material_suppliers' AS text) AS check_name
                                                                         , CAST(count(*) AS bigint) AS failed_rows
                                                                    FROM (SELECT 1
                                                                          FROM manufacturing_v2.material_suppliers AS t
                                                                          WHERE t.material_id IS NULL
                                                                             OR t.supplier_id IS NULL) AS failures)

                                                                   UNION ALL

                                                                   SELECT CAST('relationship_material_suppliers_0' AS text) AS check_name
                                                                        , CAST(count(*) AS bigint) AS failed_rows
                                                                   FROM (SELECT 1
                                                                         FROM manufacturing_v2.material_suppliers AS c
                                                                              LEFT JOIN manufacturing_v2.materials AS p ON c.material_id = p.material_id
                                                                         WHERE p.material_id IS NULL) AS failures)

                                                                  UNION ALL

                                                                  SELECT CAST('relationship_material_suppliers_1' AS text) AS check_name
                                                                       , CAST(count(*) AS bigint) AS failed_rows
                                                                  FROM (SELECT 1
                                                                        FROM manufacturing_v2.material_suppliers AS c
                                                                             LEFT JOIN manufacturing_v2.suppliers AS p ON c.supplier_id = p.supplier_id
                                                                        WHERE p.supplier_id IS NULL) AS failures)

                                                                 UNION ALL

                                                                 SELECT CAST('duplicate_bom' AS text) AS check_name
                                                                      , CAST(count(*) AS bigint) AS failed_rows
                                                                 FROM (SELECT product_id
                                                                            , material_id
                                                                       FROM manufacturing_v2.bom
                                                                       GROUP BY product_id, material_id
                                                                       HAVING count(*) > 1) AS failures)

                                                                UNION ALL

                                                                SELECT CAST('null_bom' AS text) AS check_name
                                                                     , CAST(count(*) AS bigint) AS failed_rows
                                                                FROM (SELECT 1
                                                                      FROM manufacturing_v2.bom AS t
                                                                      WHERE t.product_id IS NULL
                                                                         OR t.material_id IS NULL
                                                                         OR t.quantity_kg_per_unit IS NULL) AS failures)

                                                               UNION ALL

                                                               SELECT CAST('relationship_bom_0' AS text) AS check_name
                                                                    , CAST(count(*) AS bigint) AS failed_rows
                                                               FROM (SELECT 1
                                                                     FROM manufacturing_v2.bom AS c
                                                                          LEFT JOIN manufacturing_v2.products AS p ON c.product_id = p.product_id
                                                                     WHERE p.product_id IS NULL) AS failures)

                                                              UNION ALL

                                                              SELECT CAST('relationship_bom_1' AS text) AS check_name
                                                                   , CAST(count(*) AS bigint) AS failed_rows
                                                              FROM (SELECT 1
                                                                    FROM manufacturing_v2.bom AS c
                                                                         LEFT JOIN manufacturing_v2.materials AS p ON c.material_id = p.material_id
                                                                    WHERE p.material_id IS NULL) AS failures)

                                                             UNION ALL

                                                             SELECT CAST('duplicate_line_month_capacity' AS text) AS check_name
                                                                  , CAST(count(*) AS bigint) AS failed_rows
                                                             FROM (SELECT month_id
                                                                        , line_id
                                                                   FROM manufacturing_v2.line_month_capacity
                                                                   GROUP BY month_id, line_id
                                                                   HAVING count(*) > 1) AS failures)

                                                            UNION ALL

                                                            SELECT CAST('null_line_month_capacity' AS text) AS check_name
                                                                 , CAST(count(*) AS bigint) AS failed_rows
                                                            FROM (SELECT 1
                                                                  FROM manufacturing_v2.line_month_capacity AS t
                                                                  WHERE t.month_id IS NULL
                                                                     OR t.line_id IS NULL
                                                                     OR t.nominal_capacity_units IS NULL
                                                                     OR t.downtime_pct IS NULL
                                                                     OR t.effective_capacity_units IS NULL) AS failures)

                                                           UNION ALL

                                                           SELECT CAST('relationship_line_month_capacity_0' AS text) AS check_name
                                                                , CAST(count(*) AS bigint) AS failed_rows
                                                           FROM (SELECT 1
                                                                 FROM manufacturing_v2.line_month_capacity AS c
                                                                      LEFT JOIN manufacturing_v2.months AS p ON c.month_id = p.month_id
                                                                 WHERE p.month_id IS NULL) AS failures)

                                                          UNION ALL

                                                          SELECT CAST('relationship_line_month_capacity_1' AS text) AS check_name
                                                               , CAST(count(*) AS bigint) AS failed_rows
                                                          FROM (SELECT 1
                                                                FROM manufacturing_v2.line_month_capacity AS c
                                                                     LEFT JOIN manufacturing_v2.production_lines AS p ON c.line_id = p.line_id
                                                                WHERE p.line_id IS NULL) AS failures)

                                                         UNION ALL

                                                         SELECT CAST('duplicate_production' AS text) AS check_name
                                                              , CAST(count(*) AS bigint) AS failed_rows
                                                         FROM (SELECT production_id
                                                               FROM manufacturing_v2.production
                                                               GROUP BY production_id
                                                               HAVING count(*) > 1) AS failures)

                                                        UNION ALL

                                                        SELECT CAST('null_production' AS text) AS check_name
                                                             , CAST(count(*) AS bigint) AS failed_rows
                                                        FROM (SELECT 1
                                                              FROM manufacturing_v2.production AS t
                                                              WHERE t.production_id IS NULL
                                                                 OR t.month_id IS NULL
                                                                 OR t.product_id IS NULL
                                                                 OR t.attempted_units IS NULL
                                                                 OR t.defective_units IS NULL
                                                                 OR t.good_units IS NULL) AS failures)

                                                       UNION ALL

                                                       SELECT CAST('relationship_production_0' AS text) AS check_name
                                                            , CAST(count(*) AS bigint) AS failed_rows
                                                       FROM (SELECT 1
                                                             FROM manufacturing_v2.production AS c
                                                                  LEFT JOIN manufacturing_v2.months AS p ON c.month_id = p.month_id
                                                             WHERE p.month_id IS NULL) AS failures)

                                                      UNION ALL

                                                      SELECT CAST('relationship_production_1' AS text) AS check_name
                                                           , CAST(count(*) AS bigint) AS failed_rows
                                                      FROM (SELECT 1
                                                            FROM manufacturing_v2.production AS c
                                                                 LEFT JOIN manufacturing_v2.products AS p ON c.product_id = p.product_id
                                                            WHERE p.product_id IS NULL) AS failures)

                                                     UNION ALL

                                                     SELECT CAST('duplicate_purchase_order_lines' AS text) AS check_name
                                                          , CAST(count(*) AS bigint) AS failed_rows
                                                     FROM (SELECT po_line_id
                                                           FROM manufacturing_v2.purchase_order_lines
                                                           GROUP BY po_line_id
                                                           HAVING count(*) > 1) AS failures)

                                                    UNION ALL

                                                    SELECT CAST('null_purchase_order_lines' AS text) AS check_name
                                                         , CAST(count(*) AS bigint) AS failed_rows
                                                    FROM (SELECT 1
                                                          FROM manufacturing_v2.purchase_order_lines AS t
                                                          WHERE t.po_line_id IS NULL
                                                             OR t.material_id IS NULL
                                                             OR t.supplier_id IS NULL
                                                             OR t.order_date IS NULL
                                                             OR t.expected_receipt_date IS NULL
                                                             OR t.ordered_kg IS NULL
                                                             OR t.agreed_unit_cost_eur IS NULL) AS failures)

                                                   UNION ALL

                                                   SELECT CAST('relationship_purchase_order_lines_0' AS text) AS check_name
                                                        , CAST(count(*) AS bigint) AS failed_rows
                                                   FROM (SELECT 1
                                                         FROM manufacturing_v2.purchase_order_lines AS c
                                                              LEFT JOIN manufacturing_v2.material_suppliers AS p ON c.material_id = p.material_id
                                                                                                                AND c.supplier_id = p.supplier_id
                                                         WHERE p.material_id IS NULL) AS failures)

                                                  UNION ALL

                                                  SELECT CAST('duplicate_material_receipts' AS text) AS check_name
                                                       , CAST(count(*) AS bigint) AS failed_rows
                                                  FROM (SELECT receipt_id
                                                        FROM manufacturing_v2.material_receipts
                                                        GROUP BY receipt_id
                                                        HAVING count(*) > 1) AS failures)

                                                 UNION ALL

                                                 SELECT CAST('null_material_receipts' AS text) AS check_name
                                                      , CAST(count(*) AS bigint) AS failed_rows
                                                 FROM (SELECT 1
                                                       FROM manufacturing_v2.material_receipts AS t
                                                       WHERE t.receipt_id IS NULL
                                                          OR t.po_line_id IS NULL
                                                          OR t.receipt_date IS NULL
                                                          OR t.received_kg IS NULL
                                                          OR t.landed_unit_cost_eur IS NULL
                                                          OR t.receipt_value_eur IS NULL
                                                          OR t.purchase_unit_cost_eur IS NULL
                                                          OR t.purchase_value_eur IS NULL
                                                          OR t.inbound_freight_rate_eur_per_kg IS NULL
                                                          OR t.inbound_freight_eur IS NULL
                                                          OR t.landed_receipt_value_eur IS NULL) AS failures)

                                                UNION ALL

                                                SELECT CAST('relationship_material_receipts_0' AS text) AS check_name
                                                     , CAST(count(*) AS bigint) AS failed_rows
                                                FROM (SELECT 1
                                                      FROM manufacturing_v2.material_receipts AS c
                                                           LEFT JOIN manufacturing_v2.purchase_order_lines AS p ON c.po_line_id = p.po_line_id
                                                      WHERE p.po_line_id IS NULL) AS failures)

                                               UNION ALL

                                               SELECT CAST('duplicate_material_consumption' AS text) AS check_name
                                                    , CAST(count(*) AS bigint) AS failed_rows
                                               FROM (SELECT production_id
                                                          , material_id
                                                     FROM manufacturing_v2.material_consumption
                                                     GROUP BY production_id, material_id
                                                     HAVING count(*) > 1) AS failures)

                                              UNION ALL

                                              SELECT CAST('null_material_consumption' AS text) AS check_name
                                                   , CAST(count(*) AS bigint) AS failed_rows
                                              FROM (SELECT 1
                                                    FROM manufacturing_v2.material_consumption AS t
                                                    WHERE t.production_id IS NULL
                                                       OR t.material_id IS NULL
                                                       OR t.required_kg IS NULL
                                                       OR t.extra_waste_kg IS NULL
                                                       OR t.consumed_kg IS NULL
                                                       OR t.issued_material_value_eur IS NULL
                                                       OR t.weighted_average_unit_cost_eur IS NULL
                                                       OR t.issued_purchase_material_value_eur IS NULL
                                                       OR t.issued_inbound_freight_eur IS NULL
                                                       OR t.weighted_average_purchase_unit_cost_eur IS NULL
                                                       OR t.weighted_average_inbound_freight_unit_cost_eur IS NULL) AS failures)

                                             UNION ALL

                                             SELECT CAST('relationship_material_consumption_0' AS text) AS check_name
                                                  , CAST(count(*) AS bigint) AS failed_rows
                                             FROM (SELECT 1
                                                   FROM manufacturing_v2.material_consumption AS c
                                                        LEFT JOIN manufacturing_v2.production AS p ON c.production_id = p.production_id
                                                   WHERE p.production_id IS NULL) AS failures)

                                            UNION ALL

                                            SELECT CAST('relationship_material_consumption_1' AS text) AS check_name
                                                 , CAST(count(*) AS bigint) AS failed_rows
                                            FROM (SELECT 1
                                                  FROM manufacturing_v2.material_consumption AS c
                                                       LEFT JOIN manufacturing_v2.materials AS p ON c.material_id = p.material_id
                                                  WHERE p.material_id IS NULL) AS failures)

                                           UNION ALL

                                           SELECT CAST('duplicate_raw_material_inventory' AS text) AS check_name
                                                , CAST(count(*) AS bigint) AS failed_rows
                                           FROM (SELECT month_id
                                                      , material_id
                                                 FROM manufacturing_v2.raw_material_inventory
                                                 GROUP BY month_id, material_id
                                                 HAVING count(*) > 1) AS failures)

                                          UNION ALL

                                          SELECT CAST('null_raw_material_inventory' AS text) AS check_name
                                               , CAST(count(*) AS bigint) AS failed_rows
                                          FROM (SELECT 1
                                                FROM manufacturing_v2.raw_material_inventory AS t
                                                WHERE t.month_id IS NULL
                                                   OR t.material_id IS NULL
                                                   OR t.opening_kg IS NULL
                                                   OR t.received_kg IS NULL
                                                   OR t.consumed_kg IS NULL
                                                   OR t.closing_kg IS NULL
                                                   OR t.opening_value_eur IS NULL
                                                   OR t.receipt_value_eur IS NULL
                                                   OR t.issued_material_value_eur IS NULL
                                                   OR t.closing_value_eur IS NULL
                                                   OR t.weighted_average_unit_cost_eur IS NULL
                                                   OR t.opening_purchase_material_value_eur IS NULL
                                                   OR t.opening_inbound_freight_value_eur IS NULL
                                                   OR t.receipt_purchase_material_value_eur IS NULL
                                                   OR t.receipt_inbound_freight_value_eur IS NULL
                                                   OR t.issued_purchase_material_value_eur IS NULL
                                                   OR t.issued_inbound_freight_value_eur IS NULL
                                                   OR t.closing_purchase_material_value_eur IS NULL
                                                   OR t.closing_inbound_freight_value_eur IS NULL
                                                   OR t.landed_receipt_value_eur IS NULL
                                                   OR t.weighted_average_purchase_unit_cost_eur IS NULL
                                                   OR t.weighted_average_inbound_freight_unit_cost_eur IS NULL) AS failures)

                                         UNION ALL

                                         SELECT CAST('relationship_raw_material_inventory_0' AS text) AS check_name
                                              , CAST(count(*) AS bigint) AS failed_rows
                                         FROM (SELECT 1
                                               FROM manufacturing_v2.raw_material_inventory AS c
                                                    LEFT JOIN manufacturing_v2.months AS p ON c.month_id = p.month_id
                                               WHERE p.month_id IS NULL) AS failures)

                                        UNION ALL

                                        SELECT CAST('relationship_raw_material_inventory_1' AS text) AS check_name
                                             , CAST(count(*) AS bigint) AS failed_rows
                                        FROM (SELECT 1
                                              FROM manufacturing_v2.raw_material_inventory AS c
                                                   LEFT JOIN manufacturing_v2.materials AS p ON c.material_id = p.material_id
                                              WHERE p.material_id IS NULL) AS failures)

                                       UNION ALL

                                       SELECT CAST('duplicate_manufacturing_costs' AS text) AS check_name
                                            , CAST(count(*) AS bigint) AS failed_rows
                                       FROM (SELECT month_id
                                                  , line_id
                                             FROM manufacturing_v2.manufacturing_costs
                                             GROUP BY month_id, line_id
                                             HAVING count(*) > 1) AS failures)

                                      UNION ALL

                                      SELECT CAST('null_manufacturing_costs' AS text) AS check_name
                                           , CAST(count(*) AS bigint) AS failed_rows
                                      FROM (SELECT 1
                                            FROM manufacturing_v2.manufacturing_costs AS t
                                            WHERE t.month_id IS NULL
                                               OR t.line_id IS NULL
                                               OR t.attempted_units IS NULL
                                               OR t.labor_hours IS NULL
                                               OR t.hourly_rate_eur IS NULL
                                               OR t.energy_kwh IS NULL
                                               OR t.energy_tariff_eur IS NULL
                                               OR t.labor_cost_eur IS NULL
                                               OR t.energy_cost_eur IS NULL
                                               OR t.manufacturing_overhead_eur IS NULL
                                               OR t.total_conversion_cost_eur IS NULL
                                               OR t.idle_cost_eur IS NULL
                                               OR t.production_labor_hours IS NULL
                                               OR t.support_labor_hours IS NULL
                                               OR t.activity_energy_kwh IS NULL
                                               OR t.base_energy_kwh IS NULL
                                               OR t.production_labor_cost_eur IS NULL
                                               OR t.support_labor_cost_eur IS NULL
                                               OR t.activity_energy_cost_eur IS NULL
                                               OR t.standby_energy_cost_eur IS NULL
                                               OR t.idle_labor_cost_eur IS NULL
                                               OR t.idle_energy_cost_eur IS NULL
                                               OR t.idle_overhead_cost_eur IS NULL) AS failures)

                                     UNION ALL

                                     SELECT CAST('relationship_manufacturing_costs_0' AS text) AS check_name
                                          , CAST(count(*) AS bigint) AS failed_rows
                                     FROM (SELECT 1
                                           FROM manufacturing_v2.manufacturing_costs AS c
                                                LEFT JOIN manufacturing_v2.months AS p ON c.month_id = p.month_id
                                           WHERE p.month_id IS NULL) AS failures)

                                    UNION ALL

                                    SELECT CAST('relationship_manufacturing_costs_1' AS text) AS check_name
                                         , CAST(count(*) AS bigint) AS failed_rows
                                    FROM (SELECT 1
                                          FROM manufacturing_v2.manufacturing_costs AS c
                                               LEFT JOIN manufacturing_v2.line_month_capacity AS p ON c.month_id = p.month_id
                                                                                                  AND c.line_id = p.line_id
                                          WHERE p.month_id IS NULL) AS failures)

                                   UNION ALL

                                   SELECT CAST('duplicate_production_cost_allocation' AS text) AS check_name
                                        , CAST(count(*) AS bigint) AS failed_rows
                                   FROM (SELECT production_id
                                         FROM manufacturing_v2.production_cost_allocation
                                         GROUP BY production_id
                                         HAVING count(*) > 1) AS failures)

                                  UNION ALL

                                  SELECT CAST('null_production_cost_allocation' AS text) AS check_name
                                       , CAST(count(*) AS bigint) AS failed_rows
                                  FROM (SELECT 1
                                        FROM manufacturing_v2.production_cost_allocation AS t
                                        WHERE t.production_id IS NULL
                                           OR t.month_id IS NULL
                                           OR t.product_id IS NULL
                                           OR t.line_id IS NULL
                                           OR t.attempted_units IS NULL
                                           OR t.good_units IS NULL
                                           OR t.material_cost_eur IS NULL
                                           OR t.labor_cost_eur IS NULL
                                           OR t.energy_cost_eur IS NULL
                                           OR t.manufacturing_overhead_eur IS NULL
                                           OR t.total_manufacturing_cost_eur IS NULL
                                           OR t.capitalized_production_cost_eur IS NULL
                                           OR t.production_loss_expense_eur IS NULL
                                           OR t.good_unit_manufacturing_cost_eur IS NULL
                                           OR t.production_labor_cost_eur IS NULL
                                           OR t.support_labor_cost_eur IS NULL
                                           OR t.activity_energy_cost_eur IS NULL
                                           OR t.standby_energy_cost_eur IS NULL
                                           OR t.purchase_material_cost_eur IS NULL
                                           OR t.inbound_freight_cost_eur IS NULL
                                           OR t.capitalized_material_cost_eur IS NULL
                                           OR t.capitalized_inbound_freight_cost_eur IS NULL
                                           OR t.capitalized_labor_cost_eur IS NULL
                                           OR t.capitalized_energy_cost_eur IS NULL
                                           OR t.capitalized_overhead_cost_eur IS NULL
                                           OR t.material_production_loss_expense_eur IS NULL
                                           OR t.inbound_freight_production_loss_expense_eur IS NULL
                                           OR t.labor_production_loss_expense_eur IS NULL
                                           OR t.energy_production_loss_expense_eur IS NULL
                                           OR t.overhead_production_loss_expense_eur IS NULL) AS failures)

                                 UNION ALL

                                 SELECT CAST('relationship_production_cost_allocation_0' AS text) AS check_name
                                      , CAST(count(*) AS bigint) AS failed_rows
                                 FROM (SELECT 1
                                       FROM manufacturing_v2.production_cost_allocation AS c
                                            LEFT JOIN manufacturing_v2.production AS p ON c.production_id = p.production_id
                                                                                      AND c.month_id = p.month_id
                                                                                      AND c.product_id = p.product_id
                                       WHERE p.production_id IS NULL) AS failures)

                                UNION ALL

                                SELECT CAST('relationship_production_cost_allocation_1' AS text) AS check_name
                                     , CAST(count(*) AS bigint) AS failed_rows
                                FROM (SELECT 1
                                      FROM manufacturing_v2.production_cost_allocation AS c
                                           LEFT JOIN manufacturing_v2.products AS p ON c.product_id = p.product_id
                                                                                   AND c.line_id = p.line_id
                                      WHERE p.product_id IS NULL) AS failures)

                               UNION ALL

                               SELECT CAST('relationship_production_cost_allocation_2' AS text) AS check_name
                                    , CAST(count(*) AS bigint) AS failed_rows
                               FROM (SELECT 1
                                     FROM manufacturing_v2.production_cost_allocation AS c
                                          LEFT JOIN manufacturing_v2.manufacturing_costs AS p ON c.month_id = p.month_id
                                                                                             AND c.line_id = p.line_id
                                     WHERE p.month_id IS NULL) AS failures)

                              UNION ALL

                              SELECT CAST('duplicate_finished_goods_inventory' AS text) AS check_name
                                   , CAST(count(*) AS bigint) AS failed_rows
                              FROM (SELECT month_id
                                         , product_id
                                    FROM manufacturing_v2.finished_goods_inventory
                                    GROUP BY month_id, product_id
                                    HAVING count(*) > 1) AS failures)

                             UNION ALL

                             SELECT CAST('null_finished_goods_inventory' AS text) AS check_name
                                  , CAST(count(*) AS bigint) AS failed_rows
                             FROM (SELECT 1
                                   FROM manufacturing_v2.finished_goods_inventory AS t
                                   WHERE t.month_id IS NULL
                                      OR t.product_id IS NULL
                                      OR t.opening_units IS NULL
                                      OR t.good_production_units IS NULL
                                      OR t.demand_units IS NULL
                                      OR t.shipped_units IS NULL
                                      OR t.unfulfilled_units IS NULL
                                      OR t.closing_units IS NULL
                                      OR t.opening_value_eur IS NULL
                                      OR t.production_value_eur IS NULL
                                      OR t.cogs_eur IS NULL
                                      OR t.closing_value_eur IS NULL
                                      OR t.weighted_average_unit_cost_eur IS NULL
                                      OR t.opening_material_value_eur IS NULL
                                      OR t.opening_inbound_freight_value_eur IS NULL
                                      OR t.opening_labor_value_eur IS NULL
                                      OR t.opening_energy_value_eur IS NULL
                                      OR t.opening_overhead_value_eur IS NULL
                                      OR t.production_material_value_eur IS NULL
                                      OR t.production_inbound_freight_value_eur IS NULL
                                      OR t.production_labor_value_eur IS NULL
                                      OR t.production_energy_value_eur IS NULL
                                      OR t.production_overhead_value_eur IS NULL
                                      OR t.closing_material_value_eur IS NULL
                                      OR t.closing_inbound_freight_value_eur IS NULL
                                      OR t.closing_labor_value_eur IS NULL
                                      OR t.closing_energy_value_eur IS NULL
                                      OR t.closing_overhead_value_eur IS NULL
                                      OR t.material_cogs_eur IS NULL
                                      OR t.inbound_freight_cogs_eur IS NULL
                                      OR t.labor_cogs_eur IS NULL
                                      OR t.energy_cogs_eur IS NULL
                                      OR t.overhead_cogs_eur IS NULL) AS failures)

                            UNION ALL

                            SELECT CAST('relationship_finished_goods_inventory_0' AS text) AS check_name
                                 , CAST(count(*) AS bigint) AS failed_rows
                            FROM (SELECT 1
                                  FROM manufacturing_v2.finished_goods_inventory AS c
                                       LEFT JOIN manufacturing_v2.months AS p ON c.month_id = p.month_id
                                  WHERE p.month_id IS NULL) AS failures)

                           UNION ALL

                           SELECT CAST('relationship_finished_goods_inventory_1' AS text) AS check_name
                                , CAST(count(*) AS bigint) AS failed_rows
                           FROM (SELECT 1
                                 FROM manufacturing_v2.finished_goods_inventory AS c
                                      LEFT JOIN manufacturing_v2.production AS p ON c.month_id = p.month_id
                                                                                AND c.product_id = p.product_id
                                 WHERE p.month_id IS NULL) AS failures)

                          UNION ALL

                          SELECT CAST('duplicate_sales' AS text) AS check_name
                               , CAST(count(*) AS bigint) AS failed_rows
                          FROM (SELECT sales_line_id
                                FROM manufacturing_v2.sales
                                GROUP BY sales_line_id
                                HAVING count(*) > 1) AS failures)

                         UNION ALL

                         SELECT CAST('null_sales' AS text) AS check_name
                              , CAST(count(*) AS bigint) AS failed_rows
                         FROM (SELECT 1
                               FROM manufacturing_v2.sales AS t
                               WHERE t.sales_line_id IS NULL
                                  OR t.month_id IS NULL
                                  OR t.shipment_date IS NULL
                                  OR t.product_id IS NULL
                                  OR t.customer_id IS NULL
                                  OR t.requested_units IS NULL
                                  OR t.unfulfilled_units IS NULL
                                  OR t.units_shipped IS NULL
                                  OR t.list_unit_price_eur IS NULL
                                  OR t.discount_pct IS NULL
                                  OR t.gross_revenue_eur IS NULL
                                  OR t.discount_amount_eur IS NULL
                                  OR t.net_revenue_eur IS NULL
                                  OR t.weighted_average_unit_cost_eur IS NULL
                                  OR t.cogs_eur IS NULL
                                  OR t.material_cogs_eur IS NULL
                                  OR t.inbound_freight_cogs_eur IS NULL
                                  OR t.labor_cogs_eur IS NULL
                                  OR t.energy_cogs_eur IS NULL
                                  OR t.overhead_cogs_eur IS NULL
                                  OR t.outbound_freight_rate_eur_per_unit IS NULL
                                  OR t.outbound_freight_eur IS NULL) AS failures)

                        UNION ALL

                        SELECT CAST('relationship_sales_0' AS text) AS check_name
                             , CAST(count(*) AS bigint) AS failed_rows
                        FROM (SELECT 1
                              FROM manufacturing_v2.sales AS c
                                   LEFT JOIN manufacturing_v2.months AS p ON c.month_id = p.month_id
                              WHERE p.month_id IS NULL) AS failures)

                       UNION ALL

                       SELECT CAST('relationship_sales_1' AS text) AS check_name
                            , CAST(count(*) AS bigint) AS failed_rows
                       FROM (SELECT 1
                             FROM manufacturing_v2.sales AS c
                                  LEFT JOIN manufacturing_v2.finished_goods_inventory AS p ON c.month_id = p.month_id
                                                                                          AND c.product_id = p.product_id
                             WHERE p.month_id IS NULL) AS failures)

                      UNION ALL

                      SELECT CAST('relationship_sales_2' AS text) AS check_name
                           , CAST(count(*) AS bigint) AS failed_rows
                      FROM (SELECT 1
                            FROM manufacturing_v2.sales AS c
                                 LEFT JOIN manufacturing_v2.customers AS p ON c.customer_id = p.customer_id
                            WHERE p.customer_id IS NULL) AS failures)

                     UNION ALL

                     SELECT CAST('duplicate_operating_expenses' AS text) AS check_name
                          , CAST(count(*) AS bigint) AS failed_rows
                     FROM (SELECT month_id
                                , expense_category
                           FROM manufacturing_v2.operating_expenses
                           GROUP BY month_id, expense_category
                           HAVING count(*) > 1) AS failures)

                    UNION ALL

                    SELECT CAST('null_operating_expenses' AS text) AS check_name
                         , CAST(count(*) AS bigint) AS failed_rows
                    FROM (SELECT 1
                          FROM manufacturing_v2.operating_expenses AS t
                          WHERE t.month_id IS NULL
                             OR t.expense_category IS NULL
                             OR t.amount_eur IS NULL
                             OR t.fixed_amount_eur IS NULL
                             OR t.variable_rate_pct IS NULL
                             OR t.variable_driver_amount_eur IS NULL
                             OR t.variable_amount_eur IS NULL) AS failures)

                   UNION ALL

                   SELECT CAST('relationship_operating_expenses_0' AS text) AS check_name
                        , CAST(count(*) AS bigint) AS failed_rows
                   FROM (SELECT 1
                         FROM manufacturing_v2.operating_expenses AS c
                              LEFT JOIN manufacturing_v2.months AS p ON c.month_id = p.month_id
                         WHERE p.month_id IS NULL) AS failures)

                  UNION ALL

                  SELECT CAST('sales_dimension_join_fanout' AS text) AS check_name
                       , CAST(count(*) AS bigint) AS failed_rows
                  FROM (SELECT sales_line_id
                        FROM manufacturing_v2.bi_sales_detail
                        GROUP BY sales_line_id
                        HAVING count(*) <> 1) AS failures)

                 UNION ALL

                 SELECT CAST('sales_dimension_join_coverage' AS text) AS check_name
                      , CAST(count(*) AS bigint) AS failed_rows
                 FROM (SELECT 1
                       WHERE (SELECT count(*)
                              FROM manufacturing_v2.sales) <> (SELECT count(*)
                                                               FROM manufacturing_v2.bi_sales_detail)) AS failures)

                UNION ALL

                SELECT CAST('product_month_uniqueness' AS text) AS check_name
                     , CAST(count(*) AS bigint) AS failed_rows
                FROM (SELECT month_id
                           , product_id
                      FROM manufacturing_v2.bi_product_month_profitability
                      GROUP BY 1, 2
                      HAVING count(*) <> 1) AS failures)

               UNION ALL

               SELECT CAST('product_sales_aggregate_reconciliation' AS text) AS check_name
                    , CAST(count(*) AS bigint) AS failed_rows
               FROM (SELECT 1
                     WHERE (SELECT sum(net_revenue_eur)
                            FROM manufacturing_v2.bi_product_month_profitability) IS DISTINCT FROM (SELECT sum(net_revenue_eur)
                                                                                                    FROM manufacturing_v2.sales)
                        OR (SELECT sum(cogs_eur)
                            FROM manufacturing_v2.bi_product_month_profitability) IS DISTINCT FROM (SELECT sum(cogs_eur)
                                                                                                    FROM manufacturing_v2.sales)) AS failures)

              UNION ALL

              SELECT CAST('customer_revenue_reconciliation' AS text) AS check_name
                   , CAST(count(*) AS bigint) AS failed_rows
              FROM (SELECT 1
                    WHERE (SELECT sum(net_revenue_eur)
                           FROM manufacturing_v2.bi_customer_month_performance) IS DISTINCT FROM (SELECT sum(net_revenue_eur)
                                                                                                  FROM manufacturing_v2.sales)) AS failures)

             UNION ALL

             SELECT CAST('monthly_fact_counts' AS text) AS check_name
                  , CAST(count(*) AS bigint) AS failed_rows
             FROM (SELECT 1
                   WHERE (SELECT count(*)
                          FROM manufacturing_v2.bi_monthly_pnl) <> (SELECT count(*)
                                                                    FROM manufacturing_v2.months)) AS failures)

            UNION ALL

            SELECT CAST('five_component_cogs_exact' AS text) AS check_name
                 , CAST(count(*) AS bigint) AS failed_rows
            FROM (SELECT 1
                  FROM manufacturing_v2.sales
                  WHERE cogs_eur <> material_cogs_eur + inbound_freight_cogs_eur + labor_cogs_eur + energy_cogs_eur + overhead_cogs_eur) AS failures)

           UNION ALL

           SELECT CAST('five_component_manufacturing_exact' AS text) AS check_name
                , CAST(count(*) AS bigint) AS failed_rows
           FROM (SELECT 1
                 FROM manufacturing_v2.production_cost_allocation
                 WHERE total_manufacturing_cost_eur <> purchase_material_cost_eur + inbound_freight_cost_eur + labor_cost_eur + energy_cost_eur + manufacturing_overhead_eur) AS failures)

          UNION ALL

          SELECT CAST('line_utilization_noninteger_ratio' AS text) AS check_name
               , CAST(count(*) AS bigint) AS failed_rows
          FROM (SELECT 1
                FROM manufacturing_v2.bi_line_production_performance
                WHERE capacity_utilization_pct IS DISTINCT FROM 100.0 * attempted_units / NULLIF(effective_capacity_units, 0)) AS failures)

         UNION ALL

         SELECT CAST('weighted_defect_rate_identity' AS text) AS check_name
              , CAST(count(*) AS bigint) AS failed_rows
         FROM (WITH a AS (
                      SELECT sum(attempted_units) AS attempted
                           , sum(defective_units) AS defects
                      FROM manufacturing_v2.production
                    )
                  , b AS (
                      SELECT sum(attempted_units) AS attempted
                           , sum(defective_units) AS defects
                      FROM manufacturing_v2.bi_production_performance
                    )
                 SELECT 1
                 FROM a
                      CROSS JOIN b
                 WHERE 100.0 * a.defects / NULLIF(a.attempted, 0) IS DISTINCT FROM 100.0 * b.defects / NULLIF(b.attempted, 0)) AS failures)

        UNION ALL

        SELECT CAST('company_op_deducted_once' AS text) AS check_name
             , CAST(count(*) AS bigint) AS failed_rows
        FROM (SELECT 1
              FROM manufacturing_v2.bi_monthly_pnl
              WHERE operating_profit <> revenue - cogs - outbound_freight - selling_expenses - administrative_expenses - idle_cost - production_loss) AS failures)

       UNION ALL

       SELECT CAST('approved_phase7_live_audit' AS text) AS check_name
            , CAST(count(*) AS bigint) AS failed_rows
       FROM (SELECT 1
             FROM manufacturing_v2.audit_pnl_reconciliation
             WHERE passed IS DISTINCT FROM TRUE) AS failures)

      UNION ALL

      SELECT CAST('existing_36_checks' AS text) AS check_name
           , CAST(count(*) AS bigint) AS failed_rows
      FROM (SELECT 1
            FROM manufacturing_v2.audit_validation_results
            WHERE failed_rows <> 0) AS failures)

     UNION ALL

     SELECT CAST('fixture_detect_duplicate' AS text) AS check_name
          , CAST(count(*) AS bigint) AS failed_rows
     FROM (SELECT 1
           WHERE (SELECT count(*)
                  FROM (SELECT id
                        FROM ((VALUES (1)
                                    , (1))) AS x (id)
                        GROUP BY id
                        HAVING count(*) > 1) AS d) <> 1) AS failures)

    UNION ALL

    SELECT CAST('fixture_detect_missing_relationship' AS text) AS check_name
         , CAST(count(*) AS bigint) AS failed_rows
    FROM (SELECT 1
          WHERE (SELECT count(*)
                 FROM ((VALUES (1)
                             , (2))) AS c (id)
                      LEFT JOIN ((VALUES (1))) AS p (id) USING (id)
                 WHERE p.id IS NULL) <> 1) AS failures)

   UNION ALL

   SELECT CAST('fixture_detect_double_counted_freight' AS text) AS check_name
        , CAST(count(*) AS bigint) AS failed_rows
   FROM (SELECT 1
         WHERE NOT 10 + 2 + 3 + 4 + 5 + 2 <> 10 + 2 + 3 + 4 + 5) AS failures)

  UNION ALL

  SELECT CAST('fixture_null_and_zero_denominator' AS text) AS check_name
       , CAST(count(*) AS bigint) AS failed_rows
  FROM (SELECT 1
        WHERE 100.0 * 0 / NULLIF(0, 0) IS NOT NULL
           OR COALESCE(CAST(NULL AS numeric)
                     , 0) <> 0
           OR 100.0 * 1 / NULLIF(3, 0) NOT BETWEEN 33.3333 AND 33.3334) AS failures)

 UNION ALL

 SELECT CAST('fixture_ratio_of_sums_not_average' AS text) AS check_name
      , CAST(count(*) AS bigint) AS failed_rows
 FROM (WITH x(  n, d) AS (
              VALUES (CAST(1 AS numeric)
                    , CAST(2 AS numeric))
                   , (9, 90)
            )
         SELECT 1
         FROM x
         HAVING 100 * sum(n) / sum(d) <> 100.0 * 10 / 92
             OR avg(100 * n / d) = 100 * sum(n) / sum(d)) AS failures)

UNION ALL

SELECT CAST('fixture_detect_fanout' AS text) AS check_name
     , CAST(count(*) AS bigint) AS failed_rows
FROM (SELECT 1
      WHERE (SELECT count(*)
             FROM ((VALUES (1)
                         , (1))) AS s (id)
                  INNER JOIN ((VALUES (1)
                                    , (1)
                                    , (1))) AS c (id) USING (id)) <> 6) AS failures

ORDER BY check_name;

SELECT *
FROM manufacturing_v2.audit_pnl_reconciliation
ORDER BY period
       , metric;

WITH unsafe AS (
       SELECT count(*) AS joined_rows
       FROM manufacturing_v2.sales AS s
            INNER JOIN manufacturing_v2.production AS p USING (month_id, product_id)
            INNER JOIN manufacturing_v2.material_consumption AS c USING (production_id)
     )
   , safe AS (
       SELECT count(*) AS sales_rows
       FROM manufacturing_v2.sales
     )
  SELECT sales_rows
       , joined_rows
       , CAST(joined_rows AS numeric) / NULLIF(sales_rows, 0) AS unsafe_fanout_multiplier
  FROM safe
       CROSS JOIN unsafe
