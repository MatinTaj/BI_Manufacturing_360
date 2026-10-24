import pandas as pd

df = pd.read_csv("data/processed/production.csv")

print(df.head())
print(df.shape)
print(df.columns.tolist())

total_production = df["attempted_units"].sum()
total_defects = df["defective_units"].sum()
defect_rate = total_defects / total_production * 100

print("Total Production:", total_production)
print("Total Defects:", total_defects)
print(f"{defect_rate:.2f}%")

defects_by_product = df.groupby("product_id")['defective_units'].sum()
print(defects_by_product.sort_values(ascending=True))


product_analysis = df.groupby("product_id")[["attempted_units", "defective_units"]].sum()

product_analysis["defect_rate"] = (
    product_analysis["defective_units"]
    / product_analysis["attempted_units"] * 100
)
print(product_analysis)

monthly_analysis = df.groupby("month_id")[["attempted_units", "defective_units"]].sum()
print(monthly_analysis)

monthly_analysis["defect_rate"] = (
    monthly_analysis["defective_units"]
    / monthly_analysis["attempted_units"] * 100
)
print(monthly_analysis.round(2))

print("\nWorst 5 months:")
print (monthly_analysis.sort_values(by='defect_rate', ascending=False).head(5).round(2))

df["year"] = df["month_id"].str[:4]

yearly_analysis = df.groupby("year")[["attempted_units", "defective_units"]].sum()

yearly_analysis["defect_rate"] = (
    yearly_analysis["defective_units"]
    / yearly_analysis["attempted_units"] * 100
)
print("\nYearly Quality Comparison:")
print(yearly_analysis.round(2))

rate_2024 = yearly_analysis.loc["2024", "defect_rate"]
rate_2025 = yearly_analysis.loc["2025", "defect_rate"]

difference = rate_2025 - rate_2024

print(f"\nDefect Rate Change: {difference:+.2f} percentage points")

products = pd.read_csv("data/processed/products.csv")

print(products.head())

merged_data = df.merge(products, on="product_id", how="left")
print(merged_data.head())

line_analysis = merged_data.groupby("line_id")[["attempted_units", "defective_units"]].sum()

line_analysis["defect_rate"] = (
    line_analysis["defective_units"]
    / line_analysis["attempted_units"] * 100
)

print("\nProduction Line Analysis:")
print(line_analysis.round(2))

with pd.ExcelWriter("reports/Production_Analysis.xlsx") as writer:

    product_analysis.to_excel(writer, sheet_name="Products")
    monthly_analysis.to_excel(writer, sheet_name="Monthly")
    line_analysis.to_excel(writer, sheet_name="Production Lines")