let
    Source = fxRead("SELECT s.product_id, s.product_name, s.category, s.line_id, s.base_selling_price_eur, s.standard_labor_hours_per_attempt, s.standard_energy_kwh_per_attempt FROM manufacturing_v2.products s"),
    Typed = Table.TransformColumnTypes(Source, {{"line_id", type text}, {"category", type text}, {"product_id", type text}, {"product_name", type text}, {"base_selling_price_eur", Currency.Type}, {"standard_energy_kwh_per_attempt", type number}, {"standard_labor_hours_per_attempt", type number}}, "en-US")
in Typed
