let
    Source = fxRead("SELECT s.month_id, s.line_id, s.nominal_capacity_units, s.downtime_pct, s.effective_capacity_units FROM manufacturing_v2.line_month_capacity s"),
    Typed = Table.TransformColumnTypes(Source, {{"line_id", type text}, {"month_id", type date}, {"downtime_pct", type number}, {"nominal_capacity_units", Int64.Type}, {"effective_capacity_units", Int64.Type}}, "en-US")
in Typed
