# Official technical references

Project-specific facts and expected values come from live manufacturing_v2 data, docs/financial_model.md, the Phase 7/8B baseline and Phase 8C analyses. The following Microsoft references informed connector/calendar/filter implementation choices; they do not certify our unexecuted formulas.

- [Star schema guidance](https://learn.microsoft.com/power-bi/guidance/star-schema): dimension/fact separation and declared grains.
- [Date table guidance](https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables): unique, nonblank daily dates spanning full years.
- [PostgreSQL.Database M function](https://learn.microsoft.com/en-us/powerquery-m/postgresql-database): server:port and native SELECT/connector options.
- [USERELATIONSHIP](https://learn.microsoft.com/en-us/dax/userelationship-function-dax): activate an existing inactive relationship inside CALCULATE.
- [ALLSELECTED](https://learn.microsoft.com/en-us/dax/allselected-function-dax): cohort visual totals retain outside selections.

Microsoft documentation was checked during Phase 9A. Desktop version/connector availability and actual runtime behavior still require local acceptance tests.
