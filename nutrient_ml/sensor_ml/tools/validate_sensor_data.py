from pathlib import Path
import pandas as pd
import numpy as np


# =========================================================
# DHURANDHAR SENSOR DATA VALIDATOR
# =========================================================

CSV_PATH = Path(
    r"D:\Dhurandhar\nutrient_ml\sensor_ml\data\raw\sensor_readings.csv"
)


REQUIRED_COLUMNS = [
    "timestamp",
    "plant_id",
    "crop",
    "soil_moisture_raw",
    "rain_raw",
    "ldr_raw",
    "temperature_c",
    "humidity_pct",
    "nutrient_label",
    "image_path",
]


NUMERIC_COLUMNS = [
    "soil_moisture_raw",
    "rain_raw",
    "ldr_raw",
    "temperature_c",
    "humidity_pct",
]


VALID_LABELS = [
    "Healthy",
    "K_Deficiency",
    "N_Deficiency",
    "P_Deficiency",
]


# =========================================================
# LOAD
# =========================================================

print("======================================")
print("DHURANDHAR SENSOR DATA VALIDATOR")
print("======================================")

print()
print("CSV:")
print(CSV_PATH)

if not CSV_PATH.exists():
    raise FileNotFoundError(
        f"CSV not found:\n{CSV_PATH}"
    )

df = pd.read_csv(CSV_PATH)

print()
print("Rows:", len(df))
print("Columns:", len(df.columns))


# =========================================================
# COLUMN CHECK
# =========================================================

print()
print("Checking columns...")

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:

    print()
    print("ERROR: Missing columns:")

    for column in missing_columns:
        print("  -", column)

    raise RuntimeError(
        "CSV schema is incomplete."
    )

print("All required columns are present.")


# =========================================================
# MISSING VALUE CHECK
# =========================================================

print()
print("Checking missing values...")

missing_counts = df[
    REQUIRED_COLUMNS
].isna().sum()

has_missing = False

for column, count in missing_counts.items():

    if count > 0:

        has_missing = True

        print(
            f"  {column}: {count} missing"
        )

if not has_missing:

    print("No missing values found.")


# =========================================================
# NUMERIC CHECK
# =========================================================

print()
print("Checking numeric sensor fields...")

numeric_errors = {}

for column in NUMERIC_COLUMNS:

    converted = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    invalid = (
        converted.isna()
        & df[column].notna()
    )

    count = int(invalid.sum())

    numeric_errors[column] = count

    if count > 0:

        print(
            f"  {column}: {count} non-numeric values"
        )

if sum(numeric_errors.values()) == 0:

    print("All sensor fields are numeric.")


# =========================================================
# LABEL CHECK
# =========================================================

print()
print("Checking nutrient labels...")

invalid_labels = df[
    ~df["nutrient_label"].isin(VALID_LABELS)
]

if len(invalid_labels) > 0:

    print(
        "Invalid labels:",
        len(invalid_labels)
    )

    print(
        invalid_labels[
            "nutrient_label"
        ].value_counts()
    )

else:

    print("All nutrient labels are valid.")


# =========================================================
# DUPLICATE CHECK
# =========================================================

print()
print("Checking duplicate observations...")

duplicate_count = int(
    df.duplicated().sum()
)

print(
    "Duplicate rows:",
    duplicate_count
)


# =========================================================
# CLASS DISTRIBUTION
# =========================================================

print()
print("Nutrient class distribution:")
print("--------------------------------------")

class_counts = (
    df["nutrient_label"]
    .value_counts()
)

for label in VALID_LABELS:

    count = int(
        class_counts.get(label, 0)
    )

    print(
        f"{label:18s}: {count}"
    )


# =========================================================
# SENSOR STATISTICS
# =========================================================

print()
print("Sensor statistics:")
print("--------------------------------------")

for column in NUMERIC_COLUMNS:

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    print()
    print(column)

    if values.notna().sum() == 0:

        print("  No valid numeric data yet.")

        continue

    print(
        f"  min : {values.min():.3f}"
    )

    print(
        f"  max : {values.max():.3f}"
    )

    print(
        f"  mean: {values.mean():.3f}"
    )

    print(
        f"  std : {values.std():.3f}"
    )


# =========================================================
# FINAL STATUS
# =========================================================

print()
print("======================================")

critical_problem = (
    len(missing_columns) > 0
    or sum(numeric_errors.values()) > 0
    or len(invalid_labels) > 0
)

if critical_problem:

    print("STATUS: ⚠️ DATA NEEDS CLEANING")

else:

    print("STATUS: ✅ DATA FORMAT VALID")

print("======================================")