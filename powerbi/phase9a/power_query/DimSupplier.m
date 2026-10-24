let
    Source = fxRead("SELECT s.supplier_id, s.supplier_name, s.lead_time_days, s.on_time_delivery_target FROM manufacturing_v2.suppliers s"),
    Typed = Table.TransformColumnTypes(Source, {{"supplier_id", type text}, {"supplier_name", type text}, {"lead_time_days", Int64.Type}, {"on_time_delivery_target", type number}}, "en-US")
in Typed
