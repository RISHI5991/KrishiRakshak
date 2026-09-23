from pathlib import Path

import pandas as pd
import numpy as np


# =========================================================
# DHURANDHAR - SENSOR PREPROCESSING
# =========================================================

CSV_PATH = Path(
    r"D:\Dhurandhar\nutrient_ml\sensor_ml\data\raw\sensor_readings.csv"
)

OUTPUT_DIR = Path(
    r"D:\Dhurandhar\nutrient_ml\sensor_ml\data\processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# SENSOR COLUMNS
# =========================================================

SENSOR_COLUMNS = [
    "soil_moisture_raw",
    "rain_raw",
    "ldr_raw",
    "temperature_c",
    "humidity_pct",
]


# =========================================================
# LOAD DATA
# =========================================================

print("======================================")
print("DHURANDHAR SENSOR PREPROCESSING")
print("======================================")

print()
print("Input:")
print(CSV_PATH)


if not CSV_PATH.exists():

    raise FileNotFoundError(
        f"Sensor CSV not found:\n{CSV_PATH}"
    )


df = pd.read_csv(CSV_PATH)

print()
print("Rows:", len(df))


# =========================================================
# EMPTY DATASET CHECK
# =========================================================

if len(df) == 0:

    print()
    print("No sensor observations yet.")
    print()
    print("This is expected because the ESP32")
    print("hardware has not been connected yet.")
    print()
    print("Preprocessing pipeline is ready.")
    print()
    print("======================================")
    print("WAITING FOR REAL SENSOR DATA")
    print("======================================")

    raise SystemExit


# =========================================================
# CONVERT SENSOR VALUES
# =========================================================

for column in SENSOR_COLUMNS:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )


# =========================================================
# REMOVE INVALID SENSOR ROWS
# =========================================================

before = len(df)

df = df.dropna(
    subset=SENSOR_COLUMNS
).reset_index(drop=True)

after = len(df)

print()
print("Rows before cleaning:", before)
print("Rows after cleaning :", after)

print(
    "Rows removed:",
    before - after
)


# =========================================================
# SENSOR STATISTICS
# =========================================================

print()
print("Sensor statistics:")
print("--------------------------------------")

for column in SENSOR_COLUMNS:

    values = df[column]

    print()
    print(column)

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
# NOTE
# =========================================================

print()
print("======================================")
print("NORMALIZATION NOT APPLIED YET")
print("======================================")

print()
print(
    "We will NOT calculate final normalization "
    "statistics until real sensor data exists."
)

print(
    "The scaler must be fitted using TRAINING "
    "data only."
)

print()
print("======================================")
print("PREPROCESSING CHECK COMPLETE")
print("======================================")