let
    Source = fxRead("SELECT s.po_line_id, s.material_id, s.supplier_id, s.order_date, s.expected_receipt_date, s.ordered_kg, s.agreed_unit_cost_eur, s.received_kg, s.outstanding_kg, s.purchase_value_eur, s.inbound_freight_eur, s.landed_receipt_value_eur FROM manufacturing_v2.bi_procurement_order_status s"),
    Typed = Table.TransformColumnTypes(Source, {{"order_date", type date}, {"ordered_kg", type number}, {"po_line_id", type text}, {"material_id", type text}, {"received_kg", type number}, {"supplier_id", type text}, {"outstanding_kg", type number}, {"purchase_value_eur", type number}, {"inbound_freight_eur", type number}, {"agreed_unit_cost_eur", type number}, {"expected_receipt_date", type date}, {"landed_receipt_value_eur", type number}}, "en-US"),
    Added = Table.AddColumn(Typed, "OrderMonth", each Date.StartOfMonth([order_date]), type date)
in Added
