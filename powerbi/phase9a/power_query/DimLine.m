let
    Source = fxRead("SELECT s.line_id, s.line_name, s.monthly_capacity_units, s.support_labor_hours_per_month, s.base_energy_kwh_per_month FROM manufacturing_v2.production_lines s"),
    Typed = Table.TransformColumnTypes(Source, {{"line_id", type text}, {"line_name", type text}, {"monthly_capacity_units", Int64.Type}, {"base_energy_kwh_per_month", type number}, {"support_labor_hours_per_month", type number}}, "en-US")
in Typed
