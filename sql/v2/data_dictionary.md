# PostgreSQL v2 source dictionary

All source columns retain their names/order and are NOT NULL. Primary keys define dataset grains. Money is EUR. All CHECK expressions are in database_contract.json.

## months

Rows: 24. Grain / primary key: `month_id`.

| Column | PostgreSQL type |
|---|---|
| `month_id` | `date` |
| `year` | `integer` |
| `quarter` | `integer` |
| `month_number` | `integer` |
| `days_in_month` | `integer` |

Additional unique keys: none.

## production_lines

Rows: 3. Grain / primary key: `line_id`.

| Column | PostgreSQL type |
|---|---|
| `line_id` | `text` |
| `line_name` | `text` |
| `monthly_capacity_units` | `integer` |
| `support_labor_hours_per_month` | `numeric(18,4)` |
| `base_energy_kwh_per_month` | `numeric(18,4)` |

Additional unique keys: none.

## materials

Rows: 10. Grain / primary key: `material_id`.

| Column | PostgreSQL type |
|---|---|
| `material_id` | `text` |
| `material_name` | `text` |
| `unit` | `text` |
| `base_unit_cost_eur` | `numeric(18,4)` |

Additional unique keys: none.

## suppliers

Rows: 15. Grain / primary key: `supplier_id`.

| Column | PostgreSQL type |
|---|---|
| `supplier_id` | `text` |
| `supplier_name` | `text` |
| `lead_time_days` | `integer` |
| `on_time_delivery_target` | `numeric(9,6)` |

Additional unique keys: none.

## customers

Rows: 25. Grain / primary key: `customer_id`.

| Column | PostgreSQL type |
|---|---|
| `customer_id` | `text` |
| `customer_name` | `text` |
| `segment` | `text` |

Additional unique keys: none.

## products

Rows: 20. Grain / primary key: `product_id`.

| Column | PostgreSQL type |
|---|---|
| `product_id` | `text` |
| `product_name` | `text` |
| `category` | `text` |
| `line_id` | `text` |
| `base_selling_price_eur` | `numeric(18,2)` |
| `standard_labor_hours_per_attempt` | `numeric(18,4)` |
| `standard_energy_kwh_per_attempt` | `numeric(18,4)` |

Additional unique keys: product_id, line_id.

Foreign key: `line_id` to `erp.production_lines(line_id)`.

## material_suppliers

Rows: 30. Grain / primary key: `material_id`, `supplier_id`.

| Column | PostgreSQL type |
|---|---|
| `material_id` | `text` |
| `supplier_id` | `text` |

Additional unique keys: none.

Foreign key: `material_id` to `erp.materials(material_id)`.

Foreign key: `supplier_id` to `erp.suppliers(supplier_id)`.

## bom

Rows: 64. Grain / primary key: `product_id`, `material_id`.

| Column | PostgreSQL type |
|---|---|
| `product_id` | `text` |
| `material_id` | `text` |
| `quantity_kg_per_unit` | `numeric(18,3)` |

Additional unique keys: none.

Foreign key: `product_id` to `erp.products(product_id)`.

Foreign key: `material_id` to `erp.materials(material_id)`.

## line_month_capacity

Rows: 72. Grain / primary key: `month_id`, `line_id`.

| Column | PostgreSQL type |
|---|---|
| `month_id` | `date` |
| `line_id` | `text` |
| `nominal_capacity_units` | `integer` |
| `downtime_pct` | `numeric(9,4)` |
| `effective_capacity_units` | `integer` |

Additional unique keys: none.

Foreign key: `month_id` to `erp.months(month_id)`.

Foreign key: `line_id` to `erp.production_lines(line_id)`.

## production

Rows: 480. Grain / primary key: `production_id`.

| Column | PostgreSQL type |
|---|---|
| `production_id` | `text` |
| `month_id` | `date` |
| `product_id` | `text` |
| `attempted_units` | `integer` |
| `defective_units` | `integer` |
| `good_units` | `integer` |

Additional unique keys: month_id, product_id; production_id, month_id, product_id.

Foreign key: `month_id` to `erp.months(month_id)`.

Foreign key: `product_id` to `erp.products(product_id)`.

## purchase_order_lines

Rows: 144. Grain / primary key: `po_line_id`.

| Column | PostgreSQL type |
|---|---|
| `po_line_id` | `text` |
| `material_id` | `text` |
| `supplier_id` | `text` |
| `order_date` | `date` |
| `expected_receipt_date` | `date` |
| `ordered_kg` | `numeric(18,3)` |
| `agreed_unit_cost_eur` | `numeric(18,4)` |

Additional unique keys: none.

Foreign key: `material_id, supplier_id` to `erp.material_suppliers(material_id, supplier_id)`.

## material_receipts

Rows: 144. Grain / primary key: `receipt_id`.

| Column | PostgreSQL type |
|---|---|
| `receipt_id` | `text` |
| `po_line_id` | `text` |
| `receipt_date` | `date` |
| `received_kg` | `numeric(18,3)` |
| `landed_unit_cost_eur` | `numeric(18,8)` |
| `receipt_value_eur` | `numeric(18,2)` |
| `purchase_unit_cost_eur` | `numeric(18,4)` |
| `purchase_value_eur` | `numeric(18,2)` |
| `inbound_freight_rate_eur_per_kg` | `numeric(18,4)` |
| `inbound_freight_eur` | `numeric(18,2)` |
| `landed_receipt_value_eur` | `numeric(18,2)` |

Additional unique keys: po_line_id.

Foreign key: `po_line_id` to `erp.purchase_order_lines(po_line_id)`.

## material_consumption

Rows: 1536. Grain / primary key: `production_id`, `material_id`.

| Column | PostgreSQL type |
|---|---|
| `production_id` | `text` |
| `material_id` | `text` |
| `required_kg` | `numeric(18,3)` |
| `extra_waste_kg` | `numeric(18,3)` |
| `consumed_kg` | `numeric(18,3)` |
| `issued_material_value_eur` | `numeric(18,2)` |
| `weighted_average_unit_cost_eur` | `numeric(18,8)` |
| `issued_purchase_material_value_eur` | `numeric(18,2)` |
| `issued_inbound_freight_eur` | `numeric(18,2)` |
| `weighted_average_purchase_unit_cost_eur` | `numeric(18,8)` |
| `weighted_average_inbound_freight_unit_cost_eur` | `numeric(18,8)` |

Additional unique keys: none.

Foreign key: `production_id` to `erp.production(production_id)`.

Foreign key: `material_id` to `erp.materials(material_id)`.

## raw_material_inventory

Rows: 240. Grain / primary key: `month_id`, `material_id`.

| Column | PostgreSQL type |
|---|---|
| `month_id` | `date` |
| `material_id` | `text` |
| `opening_kg` | `numeric(18,3)` |
| `received_kg` | `numeric(18,3)` |
| `consumed_kg` | `numeric(18,3)` |
| `closing_kg` | `numeric(18,3)` |
| `opening_value_eur` | `numeric(18,2)` |
| `receipt_value_eur` | `numeric(18,2)` |
| `issued_material_value_eur` | `numeric(18,2)` |
| `closing_value_eur` | `numeric(18,2)` |
| `weighted_average_unit_cost_eur` | `numeric(18,8)` |
| `opening_purchase_material_value_eur` | `numeric(18,2)` |
| `opening_inbound_freight_value_eur` | `numeric(18,2)` |
| `receipt_purchase_material_value_eur` | `numeric(18,2)` |
| `receipt_inbound_freight_value_eur` | `numeric(18,2)` |
| `issued_purchase_material_value_eur` | `numeric(18,2)` |
| `issued_inbound_freight_value_eur` | `numeric(18,2)` |
| `closing_purchase_material_value_eur` | `numeric(18,2)` |
| `closing_inbound_freight_value_eur` | `numeric(18,2)` |
| `landed_receipt_value_eur` | `numeric(18,2)` |
| `weighted_average_purchase_unit_cost_eur` | `numeric(18,8)` |
| `weighted_average_inbound_freight_unit_cost_eur` | `numeric(18,8)` |

Additional unique keys: none.

Foreign key: `month_id` to `erp.months(month_id)`.

Foreign key: `material_id` to `erp.materials(material_id)`.

## manufacturing_costs

Rows: 72. Grain / primary key: `month_id`, `line_id`.

| Column | PostgreSQL type |
|---|---|
| `month_id` | `date` |
| `line_id` | `text` |
| `attempted_units` | `integer` |
| `labor_hours` | `numeric(18,4)` |
| `hourly_rate_eur` | `numeric(18,4)` |
| `energy_kwh` | `numeric(18,4)` |
| `energy_tariff_eur` | `numeric(18,4)` |
| `labor_cost_eur` | `numeric(18,2)` |
| `energy_cost_eur` | `numeric(18,2)` |
| `manufacturing_overhead_eur` | `numeric(18,2)` |
| `total_conversion_cost_eur` | `numeric(18,2)` |
| `idle_cost_eur` | `numeric(18,2)` |
| `production_labor_hours` | `numeric(18,4)` |
| `support_labor_hours` | `numeric(18,4)` |
| `activity_energy_kwh` | `numeric(18,4)` |
| `base_energy_kwh` | `numeric(18,4)` |
| `production_labor_cost_eur` | `numeric(18,2)` |
| `support_labor_cost_eur` | `numeric(18,2)` |
| `activity_energy_cost_eur` | `numeric(18,2)` |
| `standby_energy_cost_eur` | `numeric(18,2)` |
| `idle_labor_cost_eur` | `numeric(18,2)` |
| `idle_energy_cost_eur` | `numeric(18,2)` |
| `idle_overhead_cost_eur` | `numeric(18,2)` |

Additional unique keys: none.

Foreign key: `month_id` to `erp.months(month_id)`.

Foreign key: `month_id, line_id` to `erp.line_month_capacity(month_id, line_id)`.

## production_cost_allocation

Rows: 480. Grain / primary key: `production_id`.

| Column | PostgreSQL type |
|---|---|
| `production_id` | `text` |
| `month_id` | `date` |
| `product_id` | `text` |
| `line_id` | `text` |
| `attempted_units` | `integer` |
| `good_units` | `integer` |
| `material_cost_eur` | `numeric(18,2)` |
| `labor_cost_eur` | `numeric(18,2)` |
| `energy_cost_eur` | `numeric(18,2)` |
| `manufacturing_overhead_eur` | `numeric(18,2)` |
| `total_manufacturing_cost_eur` | `numeric(18,2)` |
| `capitalized_production_cost_eur` | `numeric(18,2)` |
| `production_loss_expense_eur` | `numeric(18,2)` |
| `good_unit_manufacturing_cost_eur` | `numeric(18,8)` |
| `production_labor_cost_eur` | `numeric(18,2)` |
| `support_labor_cost_eur` | `numeric(18,2)` |
| `activity_energy_cost_eur` | `numeric(18,2)` |
| `standby_energy_cost_eur` | `numeric(18,2)` |
| `purchase_material_cost_eur` | `numeric(18,2)` |
| `inbound_freight_cost_eur` | `numeric(18,2)` |
| `capitalized_material_cost_eur` | `numeric(18,2)` |
| `capitalized_inbound_freight_cost_eur` | `numeric(18,2)` |
| `capitalized_labor_cost_eur` | `numeric(18,2)` |
| `capitalized_energy_cost_eur` | `numeric(18,2)` |
| `capitalized_overhead_cost_eur` | `numeric(18,2)` |
| `material_production_loss_expense_eur` | `numeric(18,2)` |
| `inbound_freight_production_loss_expense_eur` | `numeric(18,2)` |
| `labor_production_loss_expense_eur` | `numeric(18,2)` |
| `energy_production_loss_expense_eur` | `numeric(18,2)` |
| `overhead_production_loss_expense_eur` | `numeric(18,2)` |

Additional unique keys: none.

Foreign key: `production_id, month_id, product_id` to `erp.production(production_id, month_id, product_id)`.

Foreign key: `product_id, line_id` to `erp.products(product_id, line_id)`.

Foreign key: `month_id, line_id` to `erp.manufacturing_costs(month_id, line_id)`.

## finished_goods_inventory

Rows: 480. Grain / primary key: `month_id`, `product_id`.

| Column | PostgreSQL type |
|---|---|
| `month_id` | `date` |
| `product_id` | `text` |
| `opening_units` | `integer` |
| `good_production_units` | `integer` |
| `demand_units` | `integer` |
| `shipped_units` | `integer` |
| `unfulfilled_units` | `integer` |
| `closing_units` | `integer` |
| `opening_value_eur` | `numeric(18,2)` |
| `production_value_eur` | `numeric(18,2)` |
| `cogs_eur` | `numeric(18,2)` |
| `closing_value_eur` | `numeric(18,2)` |
| `weighted_average_unit_cost_eur` | `numeric(18,8)` |
| `opening_material_value_eur` | `numeric(18,2)` |
| `opening_inbound_freight_value_eur` | `numeric(18,2)` |
| `opening_labor_value_eur` | `numeric(18,2)` |
| `opening_energy_value_eur` | `numeric(18,2)` |
| `opening_overhead_value_eur` | `numeric(18,2)` |
| `production_material_value_eur` | `numeric(18,2)` |
| `production_inbound_freight_value_eur` | `numeric(18,2)` |
| `production_labor_value_eur` | `numeric(18,2)` |
| `production_energy_value_eur` | `numeric(18,2)` |
| `production_overhead_value_eur` | `numeric(18,2)` |
| `closing_material_value_eur` | `numeric(18,2)` |
| `closing_inbound_freight_value_eur` | `numeric(18,2)` |
| `closing_labor_value_eur` | `numeric(18,2)` |
| `closing_energy_value_eur` | `numeric(18,2)` |
| `closing_overhead_value_eur` | `numeric(18,2)` |
| `material_cogs_eur` | `numeric(18,2)` |
| `inbound_freight_cogs_eur` | `numeric(18,2)` |
| `labor_cogs_eur` | `numeric(18,2)` |
| `energy_cogs_eur` | `numeric(18,2)` |
| `overhead_cogs_eur` | `numeric(18,2)` |

Additional unique keys: none.

Foreign key: `month_id` to `erp.months(month_id)`.

Foreign key: `month_id, product_id` to `erp.production(month_id, product_id)`.

## sales

Rows: 2596. Grain / primary key: `sales_line_id`.

| Column | PostgreSQL type |
|---|---|
| `sales_line_id` | `text` |
| `month_id` | `date` |
| `shipment_date` | `date` |
| `product_id` | `text` |
| `customer_id` | `text` |
| `requested_units` | `integer` |
| `unfulfilled_units` | `integer` |
| `units_shipped` | `integer` |
| `list_unit_price_eur` | `numeric(18,2)` |
| `discount_pct` | `numeric(9,4)` |
| `gross_revenue_eur` | `numeric(18,2)` |
| `discount_amount_eur` | `numeric(18,2)` |
| `net_revenue_eur` | `numeric(18,2)` |
| `weighted_average_unit_cost_eur` | `numeric(18,8)` |
| `cogs_eur` | `numeric(18,2)` |
| `material_cogs_eur` | `numeric(18,2)` |
| `inbound_freight_cogs_eur` | `numeric(18,2)` |
| `labor_cogs_eur` | `numeric(18,2)` |
| `energy_cogs_eur` | `numeric(18,2)` |
| `overhead_cogs_eur` | `numeric(18,2)` |
| `outbound_freight_rate_eur_per_unit` | `numeric(18,4)` |
| `outbound_freight_eur` | `numeric(18,2)` |

Additional unique keys: none.

Foreign key: `month_id` to `erp.months(month_id)`.

Foreign key: `month_id, product_id` to `erp.finished_goods_inventory(month_id, product_id)`.

Foreign key: `customer_id` to `erp.customers(customer_id)`.

## operating_expenses

Rows: 48. Grain / primary key: `month_id`, `expense_category`.

| Column | PostgreSQL type |
|---|---|
| `month_id` | `date` |
| `expense_category` | `text` |
| `amount_eur` | `numeric(18,2)` |
| `fixed_amount_eur` | `numeric(18,2)` |
| `variable_rate_pct` | `numeric(9,4)` |
| `variable_driver_amount_eur` | `numeric(18,2)` |
| `variable_amount_eur` | `numeric(18,2)` |

Additional unique keys: none.

Foreign key: `month_id` to `erp.months(month_id)`.
