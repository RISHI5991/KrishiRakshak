# Dhurandhar Flask AI Gateway

Unified inference API for all five Dhurandhar agricultural intelligence models.

## Architecture

The Flask API acts as the **common AI service layer** — the robot (ESP32), Android app, and web interface all call the same endpoints.

```
ESP32-CAM ──HTTP POST──→ /api/analyze   → M1 + M2 + M3
ESP32-S3  ──HTTP POST──→ /api/irrigation → M5
Android   ──HTTP POST──→ /api/predict/* → Individual models
Web UI    ──HTTP POST──→ /api/analyze   → Combined analysis
```

## Quick Start

### Local Development

```bash
cd services/flask-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Server starts at `http://localhost:5003`

### Docker

```bash
cd services/flask-api
docker-compose up --build
```

### Production (Gunicorn)

```bash
gunicorn --bind 0.0.0.0:5003 --workers 2 --threads 4 --timeout 120 app:app
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web UI dashboard |
| `GET` | `/api/health` | Server health + model status |
| `GET` | `/api/models` | Loaded model details |
| `GET` | `/api/classes/<model>` | Class labels (plant / disease) |
| `POST` | `/api/predict/<model>` | Single model inference |
| `POST` | `/api/analyze` | Combined M1+M2+M3 analysis |
| `POST` | `/api/irrigation` | Irrigation decision (JSON) |

Image endpoints use `multipart/form-data` with field name `image`.

## Model Discovery

The API auto-discovers model files from these locations:

| Model | Searched Paths |
|-------|---------------|
| M1 (Crop) | `krishirakshak/ml_model/AgriGuard_Model1_Final.keras`, `models/AgriGuard_Model1_Final.keras` |
| M2 (Disease) | `krishirakshak/ml_model/AgriGuard_Model2_Final.keras`, `models/AgriGuard_Model2_Final.keras` |
| M3 (Pest) | `pest_ml/checkpoints/*.pt`, `runs/detect/**/*.pt` |
| M5 (Irrigation) | `irrigation_ml/v2/models/*.joblib` |

Set `DHURANDHAR_ROOT` env var to override the project root path.

## Testing

```bash
python -m pytest tests/ -v
```

## Configuration

| Env Variable | Default | Description |
|-------------|---------|-------------|
| `DHURANDHAR_ROOT` | Auto-detected | Project root directory |
| `API_HOST` | `0.0.0.0` | Server bind address |
| `API_PORT` | `5003` | Server port |
| `DEBUG` | `false` | Flask debug mode |
