# Parameter setup and accounting map

Reuse these exact six existing disconnected tables and Value columns. The Phase 9B formulas replace only the numeric grid with fixed-decimal CURRENCY values; names, −50%/+100% range, 1-percentage-point steps and zero defaults are unchanged. Each has 151 values. No extra parameter or fact relationship is added. This range is a UI sensitivity range, not an approved forecast.

| Table | Card/slider label | Input | Financial component affected | Fixed/excluded components |
|---|---|---|---|
| ParamPrice | Net selling price change | Fraction, e.g. 0.05=5% | Net revenue; revenue-variable selling | Units, discount percentages, fixed selling/admin, all cost rates |
| ParamMaterial | Raw material purchase cost change | Fraction | Purchase-material component of recognized sales COGS | Inbound freight, other cost components, source inventory |
| ParamInbound | Inbound freight cost change | Fraction | Recognized inbound-freight COGS only | Purchase materials, outbound, source inventory |
| ParamOutbound | Outbound freight cost change | Fraction | Shipment distribution expense below GP | Manufacturing COGS and GP |
| ParamLabor | Direct production labor cost change | Fraction | Derived direct labor portion of recognized labor COGS | Support labor, overhead, source hours and inventory |
| ParamEnergy | Recognized energy cost change | Fraction | Energy component of recognized manufacturing COGS | Other components and production activity |

## Exact formulas

```dax
ParamMaterial = GENERATESERIES(CURRENCY(-0.50), CURRENCY(1.00), CURRENCY(0.01))
```

```dax
ParamInbound = GENERATESERIES(CURRENCY(-0.50), CURRENCY(1.00), CURRENCY(0.01))
```

```dax
ParamOutbound = GENERATESERIES(CURRENCY(-0.50), CURRENCY(1.00), CURRENCY(0.01))
```

```dax
ParamLabor = GENERATESERIES(CURRENCY(-0.50), CURRENCY(1.00), CURRENCY(0.01))
```

```dax
ParamEnergy = GENERATESERIES(CURRENCY(-0.50), CURRENCY(1.00), CURRENCY(0.01))
```

```dax
ParamPrice = GENERATESERIES(CURRENCY(-0.50), CURRENCY(1.00), CURRENCY(0.01))
```

Format each Value column as 0% and the selector measures as 0.0%. The CURRENCY constructor gives a fixed-decimal grid, not a requirement to display the parameter as money. Keep the same Value column and disconnected relationships. No selection or multiple selections still yields zero through SELECTEDVALUE(...,0); therefore use a single-value control and show all six selected-change cards visibly.

## Slider behavior

Use a single-value numeric/What-if slider where the installed Desktop exposes it; its selection must be one exact value, not an interval. Start at 0%, retain −50% minimum/+100% maximum and 1-point steps. If a manually defined table does not expose the single-value slider style in that Desktop version, use a Dropdown or List slicer with Single select enabled and Select all disabled. This is a complete functional fallback requiring no extra code. Do not use a Between/Before/After range slicer: it selects multiple values and the selector measure would return zero. Slider-style availability must be tested in Desktop; it has not been verified here.

Do not run the Numeric range wizard six more times if the tables already exist; it would create duplicate tables/measures. Edit each existing calculated-table expression from parameter_tables.dax, preserve its name, and apply percent formatting. Save all six at 0%, add a Reset sensitivity bookmark that captures the six parameter slicers, and ensure unrelated bookmarks do not silently change parameter states.
