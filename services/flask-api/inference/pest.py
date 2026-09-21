import time
from pathlib import Path

class PestDetector:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.model = None
        self.model_path = None
        self.error = None
        try:
            from ultralytics import YOLO
        except Exception as exc:
            self.error = f'Ultralytics not installed: {exc}'
            return

        candidates = [
            self.root / 'runs/detect/pest_ml/results/yolo26n_batch8_test/weights/best.pt',
            self.root / 'runs/detect/pest_ml/results/yolo26n_pest24_smoke/weights/best.pt',
            self.root / 'pest_ml/checkpoints/m3_pest24_best.pt',
            self.root / 'pest_ml/checkpoints/student_direct_best.pt',
        ]
        for path in candidates:
            if not path.exists():
                continue
            try:
                self.model = YOLO(str(path))
                self.model_path = path
                break
            except Exception as exc:
                self.error = f'Failed to load {path}: {exc}'
        if self.model is None and self.error is None:
            self.error = 'No supported pest detector checkpoint found.'

    @property
    def loaded(self):
        return self.model is not None

    def predict(self, image):
        if not self.loaded:
            raise RuntimeError(self.error or 'Pest model not loaded')
        t0 = time.perf_counter()
        results = self.model.predict(source=image, verbose=False, conf=0.25)
        r = results[0]
        names = r.names if hasattr(r, 'names') else {}
        detections = []
        if getattr(r, 'boxes', None) is not None:
            boxes = r.boxes
            xyxy = boxes.xyxy.cpu().numpy()
            conf = boxes.conf.cpu().numpy()
            cls = boxes.cls.cpu().numpy().astype(int)
            for box, score, cid in zip(xyxy, conf, cls):
                detections.append({
                    'class_id': int(cid),
                    'class_name': str(names.get(int(cid), int(cid))),
                    'confidence': round(float(score), 6),
                    'bbox': [round(float(x), 2) for x in box.tolist()],
                })
        return {
            'model': 'M3-pest-detector',
            'checkpoint': str(self.model_path),
            'count': len(detections),
            'detections': detections,
            'processing_time_ms': round((time.perf_counter() - t0) * 1000, 2),
        }
