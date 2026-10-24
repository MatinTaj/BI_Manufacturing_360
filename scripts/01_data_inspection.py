
from pathlib import Path
import pandas as pd

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"

# Load manufacturing dataset
df = pd.read_csv(DATA_DIR / "manufacturing_defect_dataset.csv")

# Basic data inspection
print("DATASET SHAPE:")
print(df.shape)

print("\nCOLUMN NAMES:")
print(df.columns.tolist())

print("\nDATA TYPES:")
print(df.dtypes)

print("\nMISSING VALUES:")
print(df.isnull().sum())

print("\nDUPLICATE ROWS:")
print(df.duplicated().sum())

print("\nNUMERICAL SUMMARY:")
print(df.describe().round(2))

print("\nFIRST 5 ROWS:")
print(df.head())
