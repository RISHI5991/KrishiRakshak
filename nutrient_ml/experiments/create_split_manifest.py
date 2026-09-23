from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


# =========================================================
# DHURANDHAR - REPRODUCIBLE NPK DATASET SPLIT
# =========================================================

INPUT_FILE = Path(
    r"D:\Dhurandhar\nutrient_ml\data\npk_dataset_manifest.csv"
)

OUTPUT_FILE = Path(
    r"D:\Dhurandhar\nutrient_ml\data\npk_dataset_manifest.csv"
)

SEED = 42


# =========================================================
# LOAD MASTER MANIFEST
# =========================================================

print("======================================")
print("DHURANDHAR DATASET SPLIT")
print("======================================")

df = pd.read_csv(INPUT_FILE)

print()
print("Total images:", len(df))


# =========================================================
# FIRST SPLIT
# 70% TRAIN
# 30% TEMPORARY
# =========================================================

train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    random_state=SEED,
    stratify=df["class"],
)


# =========================================================
# SECOND SPLIT
# 15% VALIDATION
# 15% TEST
#
# temp = 30%
# half of temp = 15%
# =========================================================

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=SEED,
    stratify=temp_df["class"],
)


# =========================================================
# ADD SPLIT COLUMN
# =========================================================

train_df = train_df.copy()
val_df = val_df.copy()
test_df = test_df.copy()

train_df["split"] = "train"
val_df["split"] = "val"
test_df["split"] = "test"


# =========================================================
# COMBINE
# =========================================================

final_df = pd.concat(
    [
        train_df,
        val_df,
        test_df,
    ],
    ignore_index=True,
)


# =========================================================
# SORT FOR EASY READING
# =========================================================

final_df = final_df.sort_values(
    by=["split", "class", "filename"]
).reset_index(drop=True)


# =========================================================
# SAVE
# =========================================================

final_df.to_csv(
    OUTPUT_FILE,
    index=False,
)


# =========================================================
# RESULTS
# =========================================================

print()
print("======================================")
print("SPLIT RESULTS")
print("======================================")

print()
print("Train:", len(train_df))
print("Val  :", len(val_df))
print("Test :", len(test_df))
print("Total:", len(final_df))

print()
print("Split distribution:")
print(
    final_df["split"].value_counts()
)

print()
print("Class × Split:")
print(
    pd.crosstab(
        final_df["class"],
        final_df["split"],
    )
)

print()
print("Saved:")
print(OUTPUT_FILE)

print()
print("======================================")
print("DONE")
print("======================================")