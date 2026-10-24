let
    Source = fxRead("SELECT s.period, s.revenue, s.cogs, s.gross_profit, s.outbound_freight, s.selling_expenses, s.administrative_expenses, s.idle_cost, s.production_loss, s.operating_profit, s.gross_margin_pct, s.operating_margin_pct FROM manufacturing_v2.audit_expected_pnl s"),
    Typed = Table.TransformColumnTypes(Source, {{"cogs", Currency.Type}, {"period", type text}, {"revenue", Currency.Type}, {"idle_cost", Currency.Type}, {"gross_profit", Currency.Type}, {"production_loss", Currency.Type}, {"gross_margin_pct", type number}, {"operating_profit", Currency.Type}, {"outbound_freight", Currency.Type}, {"selling_expenses", Currency.Type}, {"operating_margin_pct", type number}, {"administrative_expenses", Currency.Type}}, "en-US")
in Typed
