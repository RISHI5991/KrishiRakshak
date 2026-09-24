import numpy as np
import pandas as pd


def irrigation_score(sm, temp, hum, water_level):
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

    if water_level < 10:
        score = 0.0
    elif water_level < 20:
        score *= 0.6
    elif water_level < 30:
        score *= 0.8

    return score


def noise_free_label(sm, temp, hum, water_level):
    score = irrigation_score(
        sm,
        temp,
        hum,
        water_level,
    )

    return int(score > 2.3)


df = pd.read_csv("data/irrigation_enhanced_dataset.csv")

print("=" * 80)
print("DHURANDHAR IRRIGATION GENERATOR AUDIT")
print("=" * 80)

print("\nDataset:")
print("Rows:", len(df))
print("Features:", len(df.columns) - 1)

print("\nCurrent labels:")
print(df["irrigation_needed"].value_counts().sort_index())


# Reconstruct the noiseless generator label.
generated = np.array([
    noise_free_label(
        row.soil_moisture,
        row.temperature,
        row.humidity,
        row.water_level,
    )
    for row in df.itertuples()
])

actual = df["irrigation_needed"].to_numpy()

agreement = (generated == actual)

print("\nGenerator-label agreement:")
print(f"Agreement: {agreement.mean() * 100:.3f}%")
print(f"Disagreement: {(~agreement).mean() * 100:.3f}%")

print("\nExpected disagreement from explicit noise:")
print("Approximately 3%")

# Compare class balance without artificial noise.
print("\nNoise-free class distribution:")
vals, counts = np.unique(generated, return_counts=True)

for v, c in zip(vals, counts):
    print(
        f"  {v}: {c} "
        f"({c / len(generated) * 100:.2f}%)"
    )


# Find ambiguous / boundary cases.
scores = np.array([
    irrigation_score(
        row.soil_moisture,
        row.temperature,
        row.humidity,
        row.water_level,
    )
    for row in df.itertuples()
])

distance = np.abs(scores - 2.3)

print("\nDecision-score statistics:")
print(
    pd.Series(scores).describe().to_string()
)

print("\nClosest samples to threshold:")
closest_idx = np.argsort(distance)[:20]

cols = [
    "soil_moisture",
    "temperature",
    "humidity",
    "water_level",
]

boundary = df.iloc[closest_idx][cols].copy()
boundary["score"] = scores[closest_idx]
boundary["distance_to_threshold"] = distance[closest_idx]
boundary["noise_free_label"] = generated[closest_idx]
boundary["observed_label"] = actual[closest_idx]

print(
    boundary.to_string(index=False)
)


# Basic one-variable sensitivity.
print("\n" + "=" * 80)
print("ONE-VARIABLE SENSITIVITY")
print("=" * 80)

baseline = {
    "sm": 50,
    "temp": 27.5,
    "hum": 70,
    "water_level": 100,
}

base_score = irrigation_score(**baseline)

print("\nBaseline:")
print(baseline)
print("Score:", base_score)
print("Decision:", int(base_score > 2.3))


def show_sensitivity(name, values, key):
    print(f"\n{name}")

    for value in values:
        point = baseline.copy()
        point[key] = value

        score = irrigation_score(**point)

        print(
            f"{value:8.2f} -> "
            f"score={score:7.3f} "
            f"decision={int(score > 2.3)}"
        )


show_sensitivity(
    "Soil moisture",
    list(range(0, 101, 10)),
    "sm",
)

show_sensitivity(
    "Temperature",
    np.linspace(22, 33, 12),
    "temp",
)

show_sensitivity(
    "Humidity",
    np.linspace(60, 80, 11),
    "hum",
)

show_sensitivity(
    "Water level",
    list(range(0, 101, 10)),
    "water_level",
)

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
