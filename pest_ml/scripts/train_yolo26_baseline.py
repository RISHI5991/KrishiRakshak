from ultralytics import YOLO

model = YOLO("yolo26n.pt")

results = model.train(
    data="pest_ml/configs/pest24.yaml",

    epochs=100,
    imgsz=640,

    batch=-8,

    patience=20,

    device="mps",

    project="pest_ml/results",
    name="yolo26n_pest24_baseline",

    save=True,
    plots=True,
    verbose=True,
)

print("\n" + "=" * 80)
print("YOLO26n PEST24 BASELINE COMPLETE")
print("=" * 80)
print(results)