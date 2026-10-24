let
    Source = fxRead("SELECT s.month_id, s.expense_category, s.amount_eur, s.fixed_amount_eur, s.variable_rate_pct, s.variable_driver_amount_eur, s.variable_amount_eur FROM manufacturing_v2.operating_expenses s"),
    Typed = Table.TransformColumnTypes(Source, {{"month_id", type date}, {"amount_eur", Currency.Type}, {"expense_category", type text}, {"fixed_amount_eur", Currency.Type}, {"variable_rate_pct", type number}, {"variable_amount_eur", Currency.Type}, {"variable_driver_amount_eur", Currency.Type}}, "en-US")
in Typed
