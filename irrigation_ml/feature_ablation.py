import pandas as pd

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


DATA = "data/irrigation_enhanced_dataset.csv"

df = pd.read_csv(DATA)

y = df["irrigation_needed"]

feature_sets = {
    "raw_4": [
        "soil_moisture",
        "temperature",
        "humidity",
        "water_level",
    ],

    "raw_no_water": [
        "soil_moisture",
        "temperature",
        "humidity",
    ],

    "core_engineered": [
        "soil_moisture",
        "temperature",
        "humidity",
        "stress_index",
        "vpd_index",
        "moisture_deficit",
    ],

    "reduced_engineered": [
        "soil_moisture",
        "temperature",
        "humidity",
        "stress_index",
        "vpd_index",
    ],

    "all_12": [
        c for c in df.columns
        if c != "irrigation_needed"
    ],
}


X_full = df.drop(columns=["irrigation_needed"])

X_train_full, X_test_full, y_train, y_test = train_test_split(
    X_full,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


print("=" * 80)
print("DHURANDHAR IRRIGATION — FEATURE ABLATION")
print("=" * 80)

results = []

for name, features in feature_sets.items():

    X_train = X_train_full[features]
    X_test = X_test_full[features]

    model = HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=31,
        l2_regularization=0.1,
        random_state=42,
    )

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)
    bal = balanced_accuracy_score(y_test, pred)
    precision = precision_score(y_test, pred, zero_division=0)
    recall = recall_score(y_test, pred, zero_division=0)
    f1 = f1_score(y_test, pred, zero_division=0)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        pred,
        labels=[0, 1],
    ).ravel()

    fnr = fn / (fn + tp) if (fn + tp) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0

    print("\n" + "-" * 80)
    print(name)
    print("Features:", features)
    print(f"Accuracy          : {acc * 100:.3f}%")
    print(f"Balanced accuracy : {bal * 100:.3f}%")
    print(f"Precision         : {precision * 100:.3f}%")
    print(f"Recall            : {recall * 100:.3f}%")
    print(f"F1                : {f1 * 100:.3f}%")
    print(f"FNR               : {fnr * 100:.3f}%")
    print(f"FPR               : {fpr * 100:.3f}%")

    results.append({
        "model": name,
        "n_features": len(features),
        "accuracy": acc,
        "balanced_accuracy": bal,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fnr": fnr,
        "fpr": fpr,
        "features": ", ".join(features),
    })


out = pd.DataFrame(results).sort_values(
    "balanced_accuracy",
    ascending=False,
)

print("\n" + "=" * 80)
print("ABLATION SUMMARY")
print("=" * 80)

print(
    out[
        [
            "model",
            "n_features",
            "accuracy",
            "balanced_accuracy",
            "precision",
            "recall",
            "f1",
            "fnr",
            "fpr",
        ]
    ].to_string(index=False)
)

output = "results/feature_ablation_v1.csv"
out.to_csv(output, index=False)

print("\nSaved:", output)
print("=" * 80)
