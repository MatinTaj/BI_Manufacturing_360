let
    Source = fxRead("SELECT s.material_id, s.material_name, s.unit, s.base_unit_cost_eur FROM manufacturing_v2.materials s"),
    Typed = Table.TransformColumnTypes(Source, {{"unit", type text}, {"material_id", type text}, {"material_name", type text}, {"base_unit_cost_eur", type number}}, "en-US")
in Typed
