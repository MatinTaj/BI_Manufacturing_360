let
    Source = fxRead("SELECT s.production_id, s.month_id, s.year, s.quarter, s.product_id, s.product_name, s.category, s.line_id, s.attempted_units, s.defective_units, s.good_units, s.defect_rate_pct, s.good_yield_pct FROM manufacturing_v2.bi_production_performance s"),
    Typed = Table.TransformColumnTypes(Source, {{"year", Int64.Type}, {"line_id", type text}, {"quarter", Int64.Type}, {"category", type text}, {"month_id", type date}, {"good_units", Int64.Type}, {"product_id", type text}, {"product_name", type text}, {"production_id", type text}, {"good_yield_pct", type number}, {"attempted_units", Int64.Type}, {"defect_rate_pct", type number}, {"defective_units", Int64.Type}}, "en-US")
in Typed
