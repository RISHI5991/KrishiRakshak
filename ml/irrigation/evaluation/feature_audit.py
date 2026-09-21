import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split


DATA = "v2/data/irrigation_v21_synthetic.csv"

df = pd.read_csv(DATA)

X = df.drop(columns=["irrigation_needed"])
y = df["irrigation_needed"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)


importance = pd.Series(
    model.feature_importances_,
    index=X.columns,
).sort_values(ascending=False)


print("=" * 80)
print("V2.1 FEATURE IMPORTANCE")
print("=" * 80)

print("\nRandom Forest importance:")
print(importance.to_string())


perm = permutation_importance(
    model,
    X_test,
    y_test,
    scoring="balanced_accuracy",
    n_repeats=10,
    random_state=42,
    n_jobs=-1,
)


perm_df = pd.DataFrame({
    "mean": perm.importances_mean,
    "std": perm.importances_std,
}, index=X.columns).sort_values(
    "mean",
    ascending=False,
)

print("\nPermutation importance:")
print(perm_df.to_string())


perm_df.to_csv(
    "v2/results/feature_audit_v21.csv"
)

print(
    "\nSaved: v2/results/feature_audit_v21.csv"
)

print("=" * 80)
