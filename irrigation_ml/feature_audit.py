import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split


DATA = "data/irrigation_enhanced_dataset.csv"

df = pd.read_csv(DATA)

X = df.drop(columns=["irrigation_needed"])
y = df["irrigation_needed"]


print("=" * 80)
print("DHURANDHAR IRRIGATION V1 — FEATURE AUDIT")
print("=" * 80)

print("\nShape:")
print("Rows   :", len(df))
print("Features:", X.shape[1])

print("\nFeatures:")
for i, col in enumerate(X.columns):
    print(f"{i:2d}. {col}")


# ------------------------------------------------------------------
# Correlation with target
# ------------------------------------------------------------------

print("\n" + "=" * 80)
print("FEATURE ↔ TARGET CORRELATION")
print("=" * 80)

corr = df.corr(numeric_only=True)["irrigation_needed"].drop(
    "irrigation_needed"
)

corr = corr.reindex(
    corr.abs().sort_values(ascending=False).index
)

print(corr.to_string())


# ------------------------------------------------------------------
# Feature-to-feature correlation
# ------------------------------------------------------------------

print("\n" + "=" * 80)
print("HIGH FEATURE-TO-FEATURE CORRELATIONS")
print("=" * 80)

feature_corr = X.corr(numeric_only=True)

pairs = []

for i, a in enumerate(feature_corr.columns):
    for j, b in enumerate(feature_corr.columns):

        if j <= i:
            continue

        value = feature_corr.loc[a, b]

        if abs(value) >= 0.90:
            pairs.append(
                (a, b, value)
            )

if pairs:
    for a, b, value in sorted(
        pairs,
        key=lambda x: abs(x[2]),
        reverse=True,
    ):
        print(
            f"{a:25s} ↔ {b:25s} "
            f"corr={value:+.4f}"
        )
else:
    print("No feature pairs above |corr| >= 0.90")


# ------------------------------------------------------------------
# Random Forest importance
# ------------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)

rf.fit(X_train, y_train)

importance = pd.Series(
    rf.feature_importances_,
    index=X.columns,
).sort_values(ascending=False)


print("\n" + "=" * 80)
print("RANDOM FOREST FEATURE IMPORTANCE")
print("=" * 80)

print(importance.to_string())


# ------------------------------------------------------------------
# Permutation importance
# ------------------------------------------------------------------

print("\n" + "=" * 80)
print("PERMUTATION IMPORTANCE")
print("=" * 80)

perm = permutation_importance(
    rf,
    X_test,
    y_test,
    n_repeats=10,
    random_state=42,
    scoring="balanced_accuracy",
    n_jobs=-1,
)

perm_mean = pd.Series(
    perm.importances_mean,
    index=X.columns,
).sort_values(ascending=False)

perm_std = pd.Series(
    perm.importances_std,
    index=X.columns,
)

for feature in perm_mean.index:
    print(
        f"{feature:25s} "
        f"mean={perm_mean[feature]:+.6f} "
        f"std={perm_std[feature]:.6f}"
    )


# ------------------------------------------------------------------
# Simple redundancy groups
# ------------------------------------------------------------------

print("\n" + "=" * 80)
print("POSSIBLE REDUNDANCY GROUPS")
print("=" * 80)

for feature in importance.index:

    related = [
        other
        for other in feature_corr.columns
        if other != feature
        and abs(feature_corr.loc[feature, other]) >= 0.75
    ]

    if related:
        print(
            f"{feature:25s} -> {', '.join(related)}"
        )


# ------------------------------------------------------------------
# Save results
# ------------------------------------------------------------------

result = pd.DataFrame({
    "rf_importance": rf.feature_importances_,
    "permutation_importance": perm.importances_mean,
    "permutation_std": perm.importances_std,
}, index=X.columns)

result = result.sort_values(
    "permutation_importance",
    ascending=False,
)

output = "results/feature_audit_v1.csv"
result.to_csv(output)

print("\nSaved:", output)

print("\n" + "=" * 80)
print("FEATURE AUDIT COMPLETE")
print("=" * 80)
