let
    Bounds = fxRead("SELECT least((SELECT min(month_id) FROM manufacturing_v2.months),(SELECT min(order_date) FROM manufacturing_v2.purchase_order_lines),(SELECT min(receipt_date) FROM manufacturing_v2.material_receipts),(SELECT min(shipment_date) FROM manufacturing_v2.sales)) AS min_date, greatest((SELECT (max(month_id)+interval '1 month - 1 day')::date FROM manufacturing_v2.months),(SELECT max(expected_receipt_date) FROM manufacturing_v2.purchase_order_lines),(SELECT max(receipt_date) FROM manufacturing_v2.material_receipts),(SELECT max(shipment_date) FROM manufacturing_v2.sales)) AS max_date"),
    First = Date.StartOfYear(Date.From(Bounds{0}[min_date])),
    Last = Date.EndOfYear(Date.From(Bounds{0}[max_date])),
    Dates = Table.FromList(List.Dates(First, Duration.Days(Last-First)+1, #duration(1,0,0,0)), Splitter.SplitByNothing(), {"Date"}),
    Typed = Table.TransformColumnTypes(Dates, {{"Date", type date}}),
    Year = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
    Quarter = Table.AddColumn(Year, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    MonthNumber = Table.AddColumn(Quarter, "MonthNumber", each Date.Month([Date]), Int64.Type),
    MonthName = Table.AddColumn(MonthNumber, "MonthName", each Date.MonthName([Date], "en-US"), type text),
    MonthStart = Table.AddColumn(MonthName, "MonthStart", each Date.StartOfMonth([Date]), type date),
    YearMonth = Table.AddColumn(MonthStart, "YearMonth", each Date.ToText([Date], "yyyy-MM", "en-US"), type text),
    YearMonthSort = Table.AddColumn(YearMonth, "YearMonthSort", each [Year]*100+[MonthNumber], Int64.Type),
    Day = Table.AddColumn(YearMonthSort, "Day", each Date.Day([Date]), Int64.Type),
    DaysInMonth = Table.AddColumn(Day, "DaysInMonth", each Date.DaysInMonth([Date]), Int64.Type)
in
    DaysInMonth
