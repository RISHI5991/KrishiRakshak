import time
from pathlib import Path

class IrrigationModel:
    FEATURES = [
        'soil_moisture_previous',
        'soil_moisture',
        'soil_moisture_trend',
        'temperature',
        'humidity',
        'rain_recent',
        'vpd',
    ]

    def __init__(self, root: Path):
        self.root = Path(root)
        self.model = None
        self.model_path = None
        self.error = None
        try:
            import joblib
        except Exception as exc:
            self.error = f'joblib not installed: {exc}'
            return
        candidates = [
            self.root / 'irrigation_ml/v2/models/m3_embedded_rf.joblib',
            self.root / 'irrigation_ml/v2/models/edge_rf50.joblib',
        ]
        for path in candidates:
            if not path.exists():
                continue
            try:
                self.model = joblib.load(path)
                self.model_path = path
                break
            except Exception as exc:
                self.error = f'Failed to load {path}: {exc}'
        if self.model is None and self.error is None:
            self.error = 'No irrigation joblib model found.'

    @property
    def loaded(self):
        return self.model is not None

    def predict(self, payload: dict):
        if not self.loaded:
            raise RuntimeError(self.error or 'Irrigation model not loaded')
        t0 = time.perf_counter()
        vals = [float(payload[k]) for k in self.FEATURES]
        pred = self.model.predict([vals])[0]
        result = {'decision': str(pred), 'features': dict(zip(self.FEATURES, vals))}
        if hasattr(self.model, 'predict_proba'):
            try:
                probs = self.model.predict_proba([vals])[0]
                classes = getattr(self.model, 'classes_', range(len(probs)))
                ranked = sorted(zip(classes, probs), key=lambda x: float(x[1]), reverse=True)
                result['probabilities'] = {str(c): round(float(p), 6) for c, p in ranked}
                result['confidence'] = round(float(ranked[0][1]), 6)
            except Exception:
                pass
        result['processing_time_ms'] = round((time.perf_counter() - t0) * 1000, 2)
        return result
