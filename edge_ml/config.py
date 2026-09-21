from pathlib import Path

ROOT = Path('/Users/rishisharma/Dhurandhar')
MANIFEST_DIR = ROOT / 'edge_ml' / 'manifests'
CHECKPOINT_DIR = ROOT / 'edge_ml' / 'checkpoints'
RESULT_DIR = ROOT / 'edge_ml' / 'results'
TEACHER_CACHE_DIR = ROOT / 'edge_ml' / 'teacher_cache'

MODEL_NAME = 'mobilenetv4_conv_small.e2400_r224_in1k'
IMAGE_SIZE = 256
BATCH_SIZE = 32
NUM_WORKERS = 0
EPOCHS = 20
LEARNING_RATE = 1e-4
MIN_LR = 1e-6
LR_FACTOR = 0.5
LR_PATIENCE = 2
EARLY_STOPPING_PATIENCE = 5
DROPOUT = 0.30
SEED = 42

CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)
TEACHER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
