from pathlib import Path

import joblib
import emlearn


MODEL = Path(
    "v2/models/m3_embedded_rf.joblib"
)

OUTPUT = Path(
    "v2/firmware/m3_model_float.h"
)


model = joblib.load(MODEL)

cmodel = emlearn.convert(
    model,
    method="inline",
    dtype="float",
)

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

cmodel.save(
    file=str(OUTPUT),
    name="m3_model_float",
)

print("=" * 70)
print("M3 FLOAT C EXPORT")
print("=" * 70)

print("Python model:", MODEL.resolve())
print("C header    :", OUTPUT.resolve())
print("Trees       :", model.n_estimators)

print("=" * 70)
