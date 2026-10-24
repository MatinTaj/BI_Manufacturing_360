-- Proposed model projections: SELECT only, no views created. Query order matches model_spec.json.

-- DimProduct
SELECT s.product_id, s.product_name, s.category, s.line_id, s.base_selling_price_eur, s.standard_labor_hours_per_attempt, s.standard_energy_kwh_per_attempt FROM manufacturing_v2.products s;

-- DimCustomer
SELECT s.customer_id, s.customer_name, s.segment FROM manufacturing_v2.customers s;

-- DimMaterial
SELECT s.material_id, s.material_name, s.unit, s.base_unit_cost_eur FROM manufacturing_v2.materials s;

-- DimSupplier
SELECT s.supplier_id, s.supplier_name, s.lead_time_days, s.on_time_delivery_target FROM manufacturing_v2.suppliers s;

-- DimLine
SELECT s.line_id, s.line_name, s.monthly_capacity_units, s.support_labor_hours_per_month, s.base_energy_kwh_per_month FROM manufacturing_v2.production_lines s;

-- FactSales
SELECT s.sales_line_id, s.month_id, s.shipment_date, s.product_id, s.customer_id, s.requested_units, s.unfulfilled_units, s.units_shipped, s.list_unit_price_eur, s.discount_pct, s.gross_revenue_eur, s.discount_amount_eur, s.net_revenue_eur, s.weighted_average_unit_cost_eur, s.cogs_eur, s.material_cogs_eur, s.inbound_freight_cogs_eur, s.labor_cogs_eur, s.energy_cogs_eur, s.overhead_cogs_eur, s.outbound_freight_rate_eur_per_unit, s.outbound_freight_eur, s.product_name, s.category, s.line_id, s.customer_name, s.segment, s.net_unit_price_eur, s.gross_profit_eur, s.gross_margin_pct, s.contribution_after_outbound_eur FROM manufacturing_v2.bi_sales_detail s;

-- FactProduction
SELECT s.production_id, s.month_id, s.year, s.quarter, s.product_id, s.product_name, s.category, s.line_id, s.attempted_units, s.defective_units, s.good_units, s.defect_rate_pct, s.good_yield_pct FROM manufacturing_v2.bi_production_performance s;

-- FactManufacturing
SELECT s.production_id, s.month_id, s.product_id, s.line_id, s.attempted_units, s.good_units, s.material_cost_eur, s.labor_cost_eur, s.energy_cost_eur, s.manufacturing_overhead_eur, s.total_manufacturing_cost_eur, s.capitalized_production_cost_eur, s.production_loss_expense_eur, s.good_unit_manufacturing_cost_eur, s.production_labor_cost_eur, s.support_labor_cost_eur, s.activity_energy_cost_eur, s.standby_energy_cost_eur, s.purchase_material_cost_eur, s.inbound_freight_cost_eur, s.capitalized_material_cost_eur, s.capitalized_inbound_freight_cost_eur, s.capitalized_labor_cost_eur, s.capitalized_energy_cost_eur, s.capitalized_overhead_cost_eur, s.material_production_loss_expense_eur, s.inbound_freight_production_loss_expense_eur, s.labor_production_loss_expense_eur, s.energy_production_loss_expense_eur, s.overhead_production_loss_expense_eur, s.product_name, s.category, s.landed_material_cost_eur FROM manufacturing_v2.bi_manufacturing_cost_components s;

-- FactConversion
SELECT s.month_id, s.line_id, s.attempted_units, s.labor_hours, s.hourly_rate_eur, s.energy_kwh, s.energy_tariff_eur, s.labor_cost_eur, s.energy_cost_eur, s.manufacturing_overhead_eur, s.total_conversion_cost_eur, s.idle_cost_eur, s.production_labor_hours, s.support_labor_hours, s.activity_energy_kwh, s.base_energy_kwh, s.production_labor_cost_eur, s.support_labor_cost_eur, s.activity_energy_cost_eur, s.standby_energy_cost_eur, s.idle_labor_cost_eur, s.idle_energy_cost_eur, s.idle_overhead_cost_eur, s.line_name FROM manufacturing_v2.bi_line_manufacturing_costs s;

-- FactCapacity
SELECT s.month_id, s.line_id, s.nominal_capacity_units, s.downtime_pct, s.effective_capacity_units FROM manufacturing_v2.line_month_capacity s;

-- FactReceipts
SELECT s.receipt_id, s.po_line_id, s.receipt_date, s.received_kg, s.landed_unit_cost_eur, s.receipt_value_eur, s.purchase_unit_cost_eur, s.purchase_value_eur, s.inbound_freight_rate_eur_per_kg, s.inbound_freight_eur, s.landed_receipt_value_eur, s.material_id, s.supplier_id, s.order_date, s.expected_receipt_date, s.agreed_unit_cost_eur, s.material_name, s.supplier_name, s.on_time, s.actual_lead_time_days FROM manufacturing_v2.bi_procurement_receipts s;

-- FactPurchaseOrders
SELECT s.po_line_id, s.material_id, s.supplier_id, s.order_date, s.expected_receipt_date, s.ordered_kg, s.agreed_unit_cost_eur, s.received_kg, s.outstanding_kg, s.purchase_value_eur, s.inbound_freight_eur, s.landed_receipt_value_eur FROM manufacturing_v2.bi_procurement_order_status s;

-- FactRawInventory
SELECT s.month_id, s.material_id, s.opening_kg, s.received_kg, s.consumed_kg, s.closing_kg, s.opening_value_eur, s.receipt_value_eur, s.issued_material_value_eur, s.closing_value_eur, s.weighted_average_unit_cost_eur, s.opening_purchase_material_value_eur, s.opening_inbound_freight_value_eur, s.receipt_purchase_material_value_eur, s.receipt_inbound_freight_value_eur, s.issued_purchase_material_value_eur, s.issued_inbound_freight_value_eur, s.closing_purchase_material_value_eur, s.closing_inbound_freight_value_eur, s.landed_receipt_value_eur, s.weighted_average_purchase_unit_cost_eur, s.weighted_average_inbound_freight_unit_cost_eur, s.material_name, s.unit FROM manufacturing_v2.bi_raw_material_inventory s;

-- FactFGInventory
SELECT s.month_id, s.product_id, s.opening_units, s.good_production_units, s.demand_units, s.shipped_units, s.unfulfilled_units, s.closing_units, s.opening_value_eur, s.production_value_eur, s.cogs_eur, s.closing_value_eur, s.weighted_average_unit_cost_eur, s.opening_material_value_eur, s.opening_inbound_freight_value_eur, s.opening_labor_value_eur, s.opening_energy_value_eur, s.opening_overhead_value_eur, s.production_material_value_eur, s.production_inbound_freight_value_eur, s.production_labor_value_eur, s.production_energy_value_eur, s.production_overhead_value_eur, s.closing_material_value_eur, s.closing_inbound_freight_value_eur, s.closing_labor_value_eur, s.closing_energy_value_eur, s.closing_overhead_value_eur, s.material_cogs_eur, s.inbound_freight_cogs_eur, s.labor_cogs_eur, s.energy_cogs_eur, s.overhead_cogs_eur, s.product_name, s.category, s.line_id FROM manufacturing_v2.bi_finished_goods_inventory s;

-- FactOpex
SELECT s.month_id, s.expense_category, s.amount_eur, s.fixed_amount_eur, s.variable_rate_pct, s.variable_driver_amount_eur, s.variable_amount_eur FROM manufacturing_v2.operating_expenses s;

-- FactConsumption
SELECT c.production_id, c.material_id, c.required_kg, c.extra_waste_kg, c.consumed_kg, c.issued_material_value_eur, c.weighted_average_unit_cost_eur, c.issued_purchase_material_value_eur, c.issued_inbound_freight_eur, c.weighted_average_purchase_unit_cost_eur, c.weighted_average_inbound_freight_unit_cost_eur, c.month_id, c.product_id, c.product_name, c.material_name, p.line_id FROM manufacturing_v2.bi_material_consumption c JOIN manufacturing_v2.products p ON p.product_id=c.product_id;

-- RefPnL
SELECT s.period, s.revenue, s.cogs, s.gross_profit, s.outbound_freight, s.selling_expenses, s.administrative_expenses, s.idle_cost, s.production_loss, s.operating_profit, s.gross_margin_pct, s.operating_margin_pct FROM manufacturing_v2.audit_expected_pnl s;

-- RefMonthlyPnL
SELECT s.month_id, s.year, s.quarter, s.revenue, s.cogs, s.gross_profit, s.outbound_freight, s.selling_expenses, s.administrative_expenses, s.idle_cost, s.production_loss, s.operating_profit, s.gross_margin_pct, s.operating_margin_pct FROM manufacturing_v2.bi_monthly_pnl s;
