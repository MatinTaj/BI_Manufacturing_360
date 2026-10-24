let
    Source = fxRead("SELECT s.customer_id, s.customer_name, s.segment FROM manufacturing_v2.customers s"),
    Typed = Table.TransformColumnTypes(Source, {{"segment", type text}, {"customer_id", type text}, {"customer_name", type text}}, "en-US")
in Typed
