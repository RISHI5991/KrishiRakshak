from pathlib import Path
from .classifier import KerasClassifier
from .pest import PestDetector
from .irrigation import IrrigationModel


def build_registry(root: Path):
    root = Path(root)

    # Search for Keras models in multiple possible locations
    candidates = {
        'm1': [
            root / 'krishirakshak/ml_model/AgriGuard_Model1_Final.keras',
            root / 'ml_model/AgriGuard_Model1_Final.keras',
            root / 'models/AgriGuard_Model1_Final.keras',
        ],
        'm2': [
            root / 'krishirakshak/ml_model/AgriGuard_Model2_Final.keras',
            root / 'ml_model/AgriGuard_Model2_Final.keras',
            root / 'models/AgriGuard_Model2_Final.keras',
        ],
    }

    def first_existing(paths):
        for p in paths:
            if p.exists():
                return p
        return paths[0]

    return {
        'm1': KerasClassifier('M1 — Crop/Plant Classification', first_existing(candidates['m1']), root, 'm1'),
        'm2': KerasClassifier('M2 — Disease Classification', first_existing(candidates['m2']), root, 'm2'),
        'm3': PestDetector(root),
        'irrigation': IrrigationModel(root),
    }
