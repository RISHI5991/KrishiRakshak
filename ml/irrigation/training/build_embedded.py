from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import emlearn

from sklearn.ensemble import RandomForestClassifier


DATA = Path("v2/data/irrigation_v21_synthetic.csv")

FEATURES = [
    "soil_moisture_previous",
    "soil_moisture",
    "soil_moisture_trend",
    "temperature",
    "humidity",
    "rain_recent",
    "vpd",
]

TARGET = "irrigation_needed"


def calculate_vpd(temp_c, humidity):
    saturation_vp = (
        0.6108
        * np.exp(
            (17.27 * temp_c) /
            (temp_c + 237.3)
        )
    )

    return saturation_vp * (
        1.0 - humidity / 100.0
    )


def add_noise(
    X,
    soil_std,
    temp_std,
    humidity_std,
    seed,
):
    rng = np.random.default_rng(seed)

    out = X.copy()

    prev = (
        out["soil_moisture_previous"].to_numpy()
        + rng.normal(
            0,
            soil_std,
            len(out),
        )
    )

    current = (
        out["soil_moisture"].to_numpy()
        + rng.normal(
            0,
            soil_std,
            len(out),
        )
    )

    out["soil_moisture_previous"] = np.clip(
        prev,
        0,
        100,
    )

    out["soil_moisture"] = np.clip(
        current,
        0,
        100,
    )

    out["soil_moisture_trend"] = (
        out["soil_moisture"]
        - out["soil_moisture_previous"]
    )

    out["temperature"] = (
        out["temperature"].to_numpy()
        + rng.normal(
            0,
            temp_std,
            len(out),
        )
    )

    out["humidity"] = np.clip(
        out["humidity"].to_numpy()
        + rng.normal(
            0,
            humidity_std,
            len(out),
        ),
        0,
        100,
    )

    out["vpd"] = calculate_vpd(
        out["temperature"].to_numpy(),
        out["humidity"].to_numpy(),
    )

    return out


df = pd.read_csv(DATA)

X = df[FEATURES]
y = df[TARGET]


# ------------------------------------------------------------
# Build robust training data
# ------------------------------------------------------------

X_mild = add_noise(
    X,
    1.0,
    0.25,
    1.5,
    100,
)

X_moderate = add_noise(
    X,
    2.0,
    0.50,
    3.0,
    200,
)

X_train = pd.concat(
    [
        X,
        X_mild,
        X_moderate,
    ],
    ignore_index=True,
)

y_train = pd.concat(
    [
        y,
        y,
        y,
    ],
    ignore_index=True,
)


# ------------------------------------------------------------
# Compact embedded model
# ------------------------------------------------------------

model = RandomForestClassifier(
    n_estimators=50,
    max_depth=8,
    min_samples_leaf=1,
    max_features="sqrt",
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)

model.fit(
    X_train,
    y_train,
)


# ------------------------------------------------------------
# Save Python artifact
# ------------------------------------------------------------

model_path = Path(
    "v2/models/m3_embedded_rf.joblib"
)

joblib.dump(
    model,
    model_path,
)


# ------------------------------------------------------------
# Export C code
# ------------------------------------------------------------

cmodel = emlearn.convert(
    model,
    method="inline",
)

header_path = Path(
    "v2/firmware/m3_model.h"
)

header_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

cmodel.save(
    file=str(header_path),
    name="m3_model",
)


print("=" * 80)
print("DHURANDHAR M3 EMBEDDED MODEL BUILT")
print("=" * 80)

print("Python model :", model_path.resolve())
print("C header     :", header_path.resolve())
print("Trees        :", model.n_estimators)
print("Max depth    :", model.max_depth)
print("=" * 80)
