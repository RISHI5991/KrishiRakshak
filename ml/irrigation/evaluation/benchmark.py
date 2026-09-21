from pathlib import Path

import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
)

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)


DATA = Path("v2/data/irrigation_v21_synthetic.csv")
RESULTS = Path("v2/results/v21_model_benchmark.csv")


df = pd.read_csv(DATA)

target = "irrigation_needed"

X = df.drop(columns=[target])
y = df[target]


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


print("=" * 80)
print("DHURANDHAR IRRIGATION V2.1 MODEL BENCHMARK")
print("=" * 80)

print("Dataset :", DATA.resolve())
print("Rows    :", len(df))
print("Features:", X.shape[1])

print("\nSplit:")
print("Train :", len(X_train))
print("Val   :", len(X_val))
print("Test  :", len(X_test))

print("\nClass distribution:")
print(y.value_counts().sort_index())


models = {

    "RandomForest": RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=1,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    ),

    "ExtraTrees": ExtraTreesClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=1,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    ),

    "GradientBoosting": GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    ),

    "HistGradientBoosting": HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=31,
        l2_regularization=0.1,
        random_state=42,
    ),
}


results = []


for name, model in models.items():

    print("\n" + "-" * 80)
    print(name)
    print("-" * 80)

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

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    cv_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=cv,
        scoring="balanced_accuracy",
        n_jobs=-1,
    )

    print(f"Accuracy          : {acc * 100:.3f}%")
    print(f"Balanced accuracy : {bal * 100:.3f}%")
    print(f"Precision         : {precision * 100:.3f}%")
    print(f"Recall            : {recall * 100:.3f}%")
    print(f"F1                : {f1 * 100:.3f}%")
    print(f"FNR               : {fnr * 100:.3f}%")
    print(f"FPR               : {fpr * 100:.3f}%")
    print(
        f"5-fold CV         : "
        f"{cv_scores.mean() * 100:.3f}% "
        f"+/- {cv_scores.std() * 100:.3f}%"
    )

    results.append(
        {
            "model": name,
            "accuracy": acc,
            "balanced_accuracy": bal,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "fnr": fnr,
            "fpr": fpr,
            "cv_balanced_accuracy_mean": cv_scores.mean(),
            "cv_balanced_accuracy_std": cv_scores.std(),
        }
    )


out = pd.DataFrame(results).sort_values(
    "balanced_accuracy",
    ascending=False,
)

print("\n" + "=" * 80)
print("V2.1 FINAL COMPARISON")
print("=" * 80)

print(
    out[
        [
            "model",
            "accuracy",
            "balanced_accuracy",
            "precision",
            "recall",
            "f1",
            "fnr",
            "fpr",
            "cv_balanced_accuracy_mean",
        ]
    ].to_string(index=False)
)


RESULTS.parent.mkdir(
    parents=True,
    exist_ok=True,
)

out.to_csv(
    RESULTS,
    index=False,
)

print("\nSaved:", RESULTS.resolve())
print("=" * 80)
