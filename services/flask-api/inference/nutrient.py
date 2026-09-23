"""PyTorch inference adapter for the M4 nutrient-deficiency classifier."""

import time
from pathlib import Path

import numpy as np
from PIL import Image


class NutrientClassifier:
    """Load and serve the MobileNetV4 checkpoint produced by nutrient training."""

    DEFAULT_CLASSES = [
        'Healthy',
        'K_Deficiency',
        'N_Deficiency',
        'P_Deficiency',
    ]
    DEFAULT_MODEL_NAME = 'mobilenetv4_conv_small.e2400_r224_in1k'
    NORMALIZE_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    NORMALIZE_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def __init__(self, root: Path):
        self.root = Path(root)
        self.model = None
        self.model_path = None
        self.error = None
        self.labels = list(self.DEFAULT_CLASSES)
        self.input_size = 224
        self.device = None
        self._torch = None

        candidates = [
            self.root / 'nutrient_ml/models/npk_vision_baseline_v1.pt',
            self.root / 'ml/nutrient/models/npk_vision_baseline_v1.pt',
            self.root / 'models/npk_vision_baseline_v1.pt',
        ]
        checkpoint_path = next((path for path in candidates if path.exists()), None)
        if checkpoint_path is None:
            self.error = 'No nutrient classifier checkpoint found.'
            return

        try:
            import torch
            import timm
        except Exception as exc:
            self.error = f'PyTorch nutrient dependencies are not installed: {exc}'
            return

        try:
            self._torch = torch
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            checkpoint = self._load_checkpoint(checkpoint_path)
            if not isinstance(checkpoint, dict):
                raise ValueError('Checkpoint must be a dictionary containing model_state_dict.')
            state_dict = checkpoint.get('model_state_dict', checkpoint.get('state_dict'))
            if not isinstance(state_dict, dict):
                raise ValueError('Checkpoint does not contain model_state_dict.')

            self.labels = self._labels_from_checkpoint(checkpoint.get('class_to_idx'))
            self.input_size = int(checkpoint.get('img_size', self.input_size))
            model_name = checkpoint.get('model_name', self.DEFAULT_MODEL_NAME)
            self.model = timm.create_model(
                model_name,
                pretrained=False,
                num_classes=len(self.labels),
            )
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            self.model_path = checkpoint_path
        except Exception as exc:
            self.error = f'{type(exc).__name__}: {exc}'
            self.model = None

    def _load_checkpoint(self, path: Path):
        """Prefer safe tensor-only checkpoint loading on supported PyTorch versions."""
        try:
            return self._torch.load(str(path), map_location=self.device, weights_only=True)
        except TypeError:  # PyTorch versions before the weights_only argument.
            return self._torch.load(str(path), map_location=self.device)

    def _labels_from_checkpoint(self, class_to_idx) -> list[str]:
        if not isinstance(class_to_idx, dict):
            return list(self.DEFAULT_CLASSES)
        try:
            labels = [name for name, _ in sorted(class_to_idx.items(), key=lambda item: int(item[1]))]
            if labels and len(labels) == len(class_to_idx):
                return [str(label) for label in labels]
        except (TypeError, ValueError):
            pass
        return list(self.DEFAULT_CLASSES)

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def _preprocess(self, image: Image.Image):
        img = image.convert('RGB').resize((self.input_size, self.input_size), Image.LANCZOS)
        array = np.asarray(img, dtype=np.float32) / 255.0
        array = (array - self.NORMALIZE_MEAN) / self.NORMALIZE_STD
        array = np.ascontiguousarray(array.transpose(2, 0, 1))
        return self._torch.from_numpy(array).unsqueeze(0).to(self.device)

    def predict(self, image: Image.Image) -> dict:
        if not self.loaded:
            raise RuntimeError(self.error or 'Nutrient model not loaded')

        t0 = time.perf_counter()
        tensor = self._preprocess(image)
        with self._torch.inference_mode():
            probabilities = self._torch.softmax(self.model(tensor), dim=1)[0].cpu().numpy()

        class_id = int(np.argmax(probabilities))
        top_indices = np.argsort(probabilities)[::-1][:3]
        return {
            'model': 'M4-nutrient-deficiency',
            'checkpoint': str(self.model_path),
            'class_id': class_id,
            'class_name': self.labels[class_id],
            'confidence': round(float(probabilities[class_id]), 6),
            'top3': [
                {
                    'class_id': int(index),
                    'class_name': self.labels[int(index)],
                    'confidence': round(float(probabilities[int(index)]), 6),
                }
                for index in top_indices
            ],
            'input_size': [self.input_size, self.input_size],
            'processing_time_ms': round((time.perf_counter() - t0) * 1000, 2),
        }
