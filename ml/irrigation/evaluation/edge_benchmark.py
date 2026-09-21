from pathlib import Path
import time
import os

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


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


df = pd.read_csv(DATA)

X = df[FEATURES]
y = df[TARGET]


X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y,
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp,
)


def evaluate_model(name, model):

    start = time.perf_counter()

    model.fit(X_train, y_train)

    train_time = time.perf_counter() - start

    # Warm up
    for _ in range(100):
        model.predict(X_test.iloc[[0]])

    start = time.perf_counter()

    for _ in range(1000):
        model.predict(X_test.iloc[[0]])

    inference_time = (
        time.perf_counter() - start
    ) / 1000

    pred = model.predict(X_test)

    acc = accuracy_score(
        y_test,
        pred,
    )

    bal = balanced_accuracy_score(
        y_test,
        pred,
    )

    precision = precision_score(
        y_test,
        pred,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        pred,
        zero_division=0,
    )

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        pred,
        labels=[0, 1],
    ).ravel()

    fnr = (
        fn / (fn + tp)
        if (fn + tp)
        else 0
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn)
        else 0
    )

    artifact = Path(
        f"v2/models/edge_{name}.joblib"
    )

    joblib.dump(
        model,
        artifact,
    )

    size_kb = (
        artifact.stat().st_size
        / 1024
    )

    predictors = getattr(
        model,
        "_predictors",
        None,
    )

    if predictors is not None:
        complexity = len(predictors)
    else:
        complexity = getattr(
            model,
            "n_estimators",
            None,
        )

    print("\n" + "-" * 80)
    print(name)
    print("-" * 80)

    print(f"Accuracy          : {acc * 100:.3f}%")
    print(f"Balanced accuracy : {bal * 100:.3f}%")
    print(f"Precision         : {precision * 100:.3f}%")
    print(f"Recall            : {recall * 100:.3f}%")
    print(f"F1                : {f1 * 100:.3f}%")
    print(f"FNR               : {fnr * 100:.3f}%")
    print(f"FPR               : {fpr * 100:.3f}%")

    print(
        f"Training time     : "
        f"{train_time:.3f} s"
    )

    print(
        f"Inference         : "
        f"{inference_time * 1000:.4f} ms"
    )

    print(
        f"Artifact size     : "
        f"{size_kb:.1f} KB"
    )

    print(
        f"Complexity        : "
        f"{complexity}"
    )

    return {
        "model": name,
        "accuracy": acc,
        "balanced_accuracy": bal,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fnr": fnr,
        "fpr": fpr,
        "train_time_s": train_time,
        "inference_ms": inference_time * 1000,
        "artifact_kb": size_kb,
        "complexity": complexity,
    }


models = {

    "hgb300": HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=31,
        l2_regularization=0.1,
        random_state=42,
    ),

    "hgb100": HistGradientBoostingClassifier(
        max_iter=100,
        learning_rate=0.05,
        max_leaf_nodes=31,
        l2_regularization=0.1,
        random_state=42,
    ),

    "hgb50": HistGradientBoostingClassifier(
        max_iter=50,
        learning_rate=0.05,
        max_leaf_nodes=31,
        l2_regularization=0.1,
        random_state=42,
    ),

    "hgb25": HistGradientBoostingClassifier(
        max_iter=25,
        learning_rate=0.05,
        max_leaf_nodes=31,
        l2_regularization=0.1,
        random_state=42,
    ),

    "rf50": RandomForestClassifier(
        n_estimators=50,
        max_depth=8,
        min_samples_leaf=1,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    ),

    "rf25": RandomForestClassifier(
        n_estimators=25,
        max_depth=6,
        min_samples_leaf=1,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    ),
}


print("=" * 80)
print("DHURANDHAR M3 — EDGE MODEL COMPRESSION BENCHMARK")
print("=" * 80)

results = []

for name, model in models.items():
    results.append(
        evaluate_model(
            name,
            model,
        )
    )


out = pd.DataFrame(results)

out = out.sort_values(
    [
        "balanced_accuracy",
        "artifact_kb",
    ],
    ascending=[
        False,
        True,
    ],
)

print("\n" + "=" * 80)
print("EDGE MODEL SUMMARY")
print("=" * 80)

print(
    out.to_string(
        index=False
    )
)

out.to_csv(
    "v2/results/edge_model_benchmark.csv",
    index=False,
)

print(
    "\nSaved:",
    Path(
        "v2/results/edge_model_benchmark.csv"
    ).resolve(),
)

print("=" * 80)
