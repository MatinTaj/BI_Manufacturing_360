# Reference sources

Project facts and accounting: docs/financial_model.md, Phase 7/8B approved baseline, Phase 8C 49-KPI dictionary, and Phase 9A model/DAX preparation. These were inspected and the actual database was read without modifying objects.

Official Microsoft documentation checked during Phase 9B:

- [GENERATESERIES](https://learn.microsoft.com/en-us/dax/generateseries-function-dax) documents Value output and an example using CURRENCY arguments; this supports the fixed-decimal parameter grid.
- [SELECTEDVALUE](https://learn.microsoft.com/en-us/dax/selectedvalue-function-dax) defines the alternate result for zero or multiple distinct selections; this explains the zero fallback and the need for single-value controls.
- [Power BI parameters](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-what-if) describes numeric parameters and slicers. We reuse supplied table/measure names instead of running a wizard that creates duplicates.

These sources do not certify the prepared project's DAX, M or C# execution; Desktop acceptance is still required. Native single-value slider availability is version-dependent in this untested setup; a single-select dropdown/list is the supported fallback described in the guide.
