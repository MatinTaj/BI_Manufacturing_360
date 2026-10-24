// Optional Tabular Editor script; not compiled or executed in Phase 9B.
bool allowScenarioUpgrade = false;
if(!allowScenarioUpgrade) throw new System.Exception("Review target model and set allowScenarioUpgrade=true explicitly.");
var target = Model.Tables["FactSales"];
if(!target.Columns.Any(c => c.Name == "direct_labor_cogs_exposure_eur") || !target.Columns.Any(c => c.Name == "support_labor_cogs_exposure_eur")) throw new System.Exception("Upgrade FactSales query first");
var definitions = new [] {
    new [] { "Material Change %", "SELECTEDVALUE('ParamMaterial'[Value], 0)", "0.0%", "Selected independent hypothetical change; BLANK/multiple defaults to zero." },
    new [] { "Inbound Change %", "SELECTEDVALUE('ParamInbound'[Value], 0)", "0.0%", "Selected independent hypothetical change; BLANK/multiple defaults to zero." },
    new [] { "Outbound Change %", "SELECTEDVALUE('ParamOutbound'[Value], 0)", "0.0%", "Selected independent hypothetical change; BLANK/multiple defaults to zero." },
    new [] { "Labor Change %", "SELECTEDVALUE('ParamLabor'[Value], 0)", "0.0%", "Existing independent zero-default parameter. Labor affects direct production-labor exposure only." },
    new [] { "Energy Change %", "SELECTEDVALUE('ParamEnergy'[Value], 0)", "0.0%", "Selected independent hypothetical change; BLANK/multiple defaults to zero." },
    new [] { "Price Change %", "SELECTEDVALUE('ParamPrice'[Value], 0)", "0.0%", "Selected independent hypothetical change; BLANK/multiple defaults to zero." },
    new [] { "Direct Labor COGS Exposure", "IF([Complete Month Context], SUM('FactSales'[direct_labor_cogs_exposure_eur]))", "#,0.00", "Derived direct production-labor subset of booked labor COGS, reconciled through monthly inventory." },
    new [] { "Support Labor COGS Exposure", "IF([Complete Month Context], SUM('FactSales'[support_labor_cogs_exposure_eur]))", "#,0.00", "Derived support-labor subset of booked labor COGS, unchanged by the direct-labor parameter." },
    new [] { "Labor Exposure Difference", "IF([Complete Month Context], [Labor COGS] - [Direct Labor COGS Exposure] - [Support Labor COGS Exposure])", "#,0.00", "Aggregate labor less analytical parts; zero in every supported slice." },
    new [] { "Scenario Revenue", "[Net Revenue] * (1 + [Price Change %])", "#,0.00", "Static shipped units, unchanged discount percentages; proportional net-price change." },
    new [] { "Scenario Manufacturing COGS", "IF([Complete Month Context], [Material COGS] * (1 + [Material Change %]) + [Inbound Freight COGS] * (1 + [Inbound Change %]) + [Labor COGS] + [Direct Labor COGS Exposure] * [Labor Change %] + [Energy COGS] * (1 + [Energy Change %]) + [Overhead COGS])", "#,0.00", "Five recognized COGS components once; only direct labor changes, support and overhead fixed." },
    new [] { "Scenario Outbound Freight", "[Outbound Freight] * (1 + [Outbound Change %])", "#,0.00", "Shipment distribution expense, excluded from manufacturing COGS." },
    new [] { "Scenario Gross Profit", "IF([Complete Month Context], [Scenario Revenue] - [Scenario Manufacturing COGS])", "#,0.00", "Hypothetical manufacturing gross profit." },
    new [] { "Scenario Gross Margin %", "DIVIDE([Scenario Gross Profit], [Scenario Revenue])", "0.00%", "Hypothetical gross margin fraction." },
    new [] { "Scenario Selling Expenses", "IF([Company Context Valid], [Fixed Selling Expenses] + [Variable Selling Expenses] * (1 + [Price Change %]))", "#,0.00", "Fixed selling unchanged; revenue-variable selling follows price at fixed volume." },
    new [] { "Scenario Operating Expenses", "IF([Company Context Valid], [Scenario Selling Expenses] + [Administrative Expenses])", "#,0.00", "Selling plus administration, matching operating_expenses.csv; outbound and production losses remain separate." },
    new [] { "Scenario Operating Profit", "IF([Company Context Valid], [Scenario Gross Profit] - [Scenario Outbound Freight] - [Scenario Operating Expenses] - [Separately Expensed Production Costs])", "#,0.00", "Company OP with each deduction recognized once." },
    new [] { "Scenario Operating Margin %", "DIVIDE([Scenario Operating Profit], IF([Company Context Valid], [Scenario Revenue]))", "0.00%", "Hypothetical company margin fraction." },
    new [] { "Scenario GP Change", "IF([Complete Month Context], [Scenario Gross Profit] - [Gross Profit])", "#,0.00", "Absolute gross profit change from unchanged baseline." },
    new [] { "Scenario GP Change %", "DIVIDE([Scenario GP Change], [Gross Profit])", "0.00%", "Relative GP change; zero base profit returns BLANK." },
    new [] { "Scenario OP Change", "IF([Company Context Valid], [Scenario Operating Profit] - [Operating Profit])", "#,0.00", "Absolute OP change, guarded for company context." },
    new [] { "Scenario OP Change %", "DIVIDE([Scenario OP Change], [Operating Profit])", "0.00%", "Relative OP change; zero base OP returns BLANK." },
};
foreach(var d in definitions) { var existing = Model.AllMeasures.FirstOrDefault(m => m.Name == d[0]); if(existing != null && existing.Table != target) throw new System.Exception("Measure exists on another table: " + d[0]); }
foreach(var d in definitions) { var m = target.Measures.FirstOrDefault(x => x.Name == d[0]); if(m == null) m = target.AddMeasure(d[0],d[1],"12 Historical Sensitivity"); else m.Expression=d[1]; m.FormatString=d[2]; m.Description=d[3]; }
