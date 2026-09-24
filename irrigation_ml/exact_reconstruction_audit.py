import numpy as np
import pandas as pd

CSV = "data/irrigation_enhanced_dataset.csv"

df = pd.read_csv(CSV)

np.random.seed(42)

reproduced = []
base_labels = []
threshold_labels = []
thresholds = []
flip_flags = []

sensor_mismatches = []

for i, row in enumerate(df.itertuples(index=False)):

    # Reproduce generator's raw random sensors
    sm = np.random.randint(0, 101)
    temp = np.random.uniform(22, 33)
    hum = np.random.uniform(60, 80)
    wl = np.random.randint(0, 101)

    # Verify generated sensors against CSV
    if (
        int(row.soil_moisture) != sm
        or not np.isclose(row.temperature, round(temp, 2))
        or not np.isclose(row.humidity, round(hum, 2))
        or int(row.water_level) != wl
    ):
        sensor_mismatches.append(i)

    # Reproduce irrigation score
    score = 0.0

    if sm < 20:
        score += 4.0
    elif sm < 30:
        score += 3.5
    elif sm < 40:
        score += 2.5
    elif sm < 50:
        score += 1.5
    elif sm < 60:
        score += 0.8
    elif sm < 70:
        score += 0.3
    elif sm >= 80:
        score -= 3.0

    if temp > 31:
        score += 1.8
    elif temp > 29:
        score += 1.2
    elif temp > 27:
        score += 0.6
    elif temp < 23:
        score -= 0.3

    if hum < 62:
        score += 1.2
    elif hum < 65:
        score += 0.6
    elif hum > 77:
        score -= 0.4

    vpd = temp - (hum / 5.0)

    if vpd > 15:
        score += 1.5
    elif vpd > 12:
        score += 0.8

    if sm < 25 and temp > 30:
        score *= 1.3

    if sm < 30 and temp > 29 and hum < 63:
        score *= 1.2

    if wl < 10:
        score = 0.0
    elif wl < 20:
        score *= 0.6
    elif wl < 30:
        score *= 0.8

    # Deterministic decision using the fixed 2.3 threshold
    base_label = int(score > 2.3)
    base_labels.append(base_label)

    # Reproduce adaptive threshold
    threshold = 2.3 + np.random.normal(0, 0.25)
    thresholds.append(threshold)

    threshold_label = int(score > threshold)
    threshold_labels.append(threshold_label)

    # Reproduce explicit 3% flip
    flip = np.random.random() < 0.03
    flip_flags.append(flip)

    final_label = 1 - threshold_label if flip else threshold_label
    reproduced.append(final_label)


actual = df["irrigation_needed"].to_numpy()

base_labels = np.array(base_labels)
threshold_labels = np.array(threshold_labels)
reproduced = np.array(reproduced)
flip_flags = np.array(flip_flags)


print("=" * 80)
print("EXACT V1 GENERATOR RECONSTRUCTION AUDIT")
print("=" * 80)

print("\nRows:", len(df))

print("\nRAW SENSOR REPRODUCTION")
print("Sensor mismatches:", len(sensor_mismatches))

print("\nFINAL LABEL REPRODUCTION")
print(
    "Exact final-label agreement:",
    f"{np.mean(reproduced == actual) * 100:.3f}%"
)

print(
    "Final-label mismatches:",
    int(np.sum(reproduced != actual))
)

print("\nBASE 2.3 THRESHOLD")
print(
    "Agreement with observed labels:",
    f"{np.mean(base_labels == actual) * 100:.3f}%"
)

print(
    "Mismatches:",
    int(np.sum(base_labels != actual))
)

print("\nADAPTIVE THRESHOLD")
print(
    "Difference caused by adaptive threshold:",
    int(np.sum(base_labels != threshold_labels))
)

print(
    "Percentage:",
    f"{np.mean(base_labels != threshold_labels) * 100:.3f}%"
)

print("\nEXPLICIT 3% FLIP")
print(
    "Rows marked for flip:",
    int(np.sum(flip_flags))
)

print(
    "Observed flip rate:",
    f"{np.mean(flip_flags) * 100:.3f}%"
)

print("\nTHRESHOLD + FLIP → FINAL")
print(
    "Threshold decision differs from final decision:",
    int(np.sum(threshold_labels != reproduced))
)

print(
    "Percentage:",
    f"{np.mean(threshold_labels != reproduced) * 100:.3f}%"
)

print("\nTHRESHOLD STATISTICS")
print(
    pd.Series(thresholds).describe().to_string()
)

print("\n" + "=" * 80)
print("RECONSTRUCTION CHECK")
print("=" * 80)

if len(sensor_mismatches) == 0:
    print("✓ Sensor generation exactly matches CSV.")
else:
    print(
        "⚠ Sensor mismatch detected on",
        len(sensor_mismatches),
        "rows."
    )

if np.array_equal(reproduced, actual):
    print("✓ Final labels exactly reproduce the CSV.")
else:
    mismatch_ids = np.where(reproduced != actual)[0]

    print(
        "⚠ Final labels do NOT exactly reproduce the CSV."
    )

    print(
        "First mismatching rows:",
        mismatch_ids[:20].tolist()
    )

print("=" * 80)
