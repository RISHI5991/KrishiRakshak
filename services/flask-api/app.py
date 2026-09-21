import logging
import time
from pathlib import Path

from flask import Flask, request, render_template
from flask_cors import CORS

from config import Config
from utils import allowed_file, validate_image, success, error
from inference.registry import build_registry

Config.ensure_dirs()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler(Config.LOG_DIR / 'api.log'), logging.StreamHandler()],
)
logger = logging.getLogger('DhurandharAPI')

app = Flask(__name__, template_folder='templates')
CORS(app, resources={r'/api/*': {'origins': '*'}})

START_TIME = time.time()
REGISTRY = build_registry(Config.PROJECT_ROOT)


def _image_from_request():
    if 'image' not in request.files:
        raise ValueError('No image provided. Use multipart field: image')
    f = request.files['image']
    if not f.filename:
        raise ValueError('Empty filename')
    if not allowed_file(f.filename, Config.ALLOWED_EXTENSIONS):
        raise ValueError(f'Unsupported image type. Allowed: {sorted(Config.ALLOWED_EXTENSIONS)}')
    return validate_image(f, Config.MAX_FILE_SIZE)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/health')
def health():
    models = {k: bool(getattr(v, 'loaded', False)) for k, v in REGISTRY.items()}
    errors = {k: getattr(v, 'error', None) or getattr(v, 'load_error', None) for k, v in REGISTRY.items()}
    return success({
        'server': 'healthy',
        'version': 'Dhurandhar Flask AI Gateway 1.0',
        'uptime_seconds': round(time.time() - START_TIME, 1),
        'project_root': str(Config.PROJECT_ROOT),
        'models_loaded': models,
        'model_errors': errors,
    })


@app.get('/api/models')
def models():
    out = {}
    for key, obj in REGISTRY.items():
        out[key] = {
            'loaded': bool(getattr(obj, 'loaded', False)),
            'path': str(getattr(obj, 'model_path', getattr(obj, 'model', None) and 'loaded' or '')),
            'error': getattr(obj, 'error', None) or getattr(obj, 'load_error', None),
        }
        if hasattr(obj, 'labels'):
            out[key]['class_count'] = len(obj.labels)
    return success(out)


@app.get('/api/classes/<model_name>')
def classes(model_name):
    key = {'plant': 'm1', 'm1': 'm1', 'disease': 'm2', 'm2': 'm2'}.get(model_name.lower())
    if not key:
        return error('Unknown classifier. Use plant, m1, disease, or m2.', 404)
    obj = REGISTRY[key]
    if not getattr(obj, 'loaded', False):
        return error(getattr(obj, 'load_error', 'Model not loaded'), 503)
    return success({'model': key, 'classes': obj.labels, 'total_classes': len(obj.labels)})


@app.post('/api/predict/<model_name>')
def predict(model_name):
    key = {'plant': 'm1', 'm1': 'm1', 'disease': 'm2', 'm2': 'm2', 'pest': 'm3', 'm3': 'm3'}.get(model_name.lower())
    if not key:
        return error('Unknown model. Use plant, disease, or pest.', 404)
    try:
        image = _image_from_request()
        result = REGISTRY[key].predict(image)
        logger.info('%s prediction completed: %s', key, result)
        return success(result)
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        logger.exception('%s prediction failed', key)
        return error(f'Prediction failed: {exc}', 500)


@app.post('/api/analyze')
def analyze():
    try:
        image = _image_from_request()
        result = {'plant': None, 'disease': None, 'pests': None}
        failures = {}
        for key, output_key in [('m1', 'plant'), ('m2', 'disease'), ('m3', 'pests')]:
            try:
                result[output_key] = REGISTRY[key].predict(image)
            except Exception as exc:
                failures[output_key] = str(exc)
        if failures:
            result['warnings'] = failures
        return success(result)
    except ValueError as exc:
        return error(str(exc), 400)
    except Exception as exc:
        logger.exception('Combined analysis failed')
        return error(f'Analysis failed: {exc}', 500)


@app.post('/api/irrigation')
def irrigation():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error('Expected JSON body.', 400)
    missing = [k for k in REGISTRY['irrigation'].FEATURES if k not in payload]
    if missing:
        return error(f'Missing irrigation fields: {missing}', 400)
    try:
        return success(REGISTRY['irrigation'].predict(payload))
    except Exception as exc:
        logger.exception('Irrigation prediction failed')
        return error(f'Irrigation prediction failed: {exc}', 500)


@app.errorhandler(404)
def not_found(_):
    return error('Endpoint not found', 404)


@app.errorhandler(405)
def method_not_allowed(_):
    return error('Method not allowed', 405)


if __name__ == '__main__':
    print('=' * 72)
    print('DHURANDHAR — FLASK AI GATEWAY')
    print('=' * 72)
    print(f'Project root: {Config.PROJECT_ROOT}')
    for key, obj in REGISTRY.items():
        loaded = bool(getattr(obj, 'loaded', False))
        detail = getattr(obj, 'model_path', '') or getattr(obj, 'model_path', '')
        print(f'{key:12} : {"READY" if loaded else "NOT READY"} {detail}')
    print(f'Open: http://localhost:{Config.PORT}')
    print('=' * 72)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=Config.THREADED)
