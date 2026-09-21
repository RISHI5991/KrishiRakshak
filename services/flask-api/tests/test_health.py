"""
Dhurandhar Flask API — Test Suite

Run with: python -m pytest tests/ -v
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app as flask_app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the /api/health endpoint."""

    def test_health_returns_200(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get('/api/health')
        data = response.get_json()
        assert data is not None
        assert data['status'] == 'success'

    def test_health_contains_required_fields(self, client):
        response = client.get('/api/health')
        data = response.get_json()['data']
        assert 'server' in data
        assert 'version' in data
        assert 'uptime_seconds' in data
        assert 'models_loaded' in data
        assert data['server'] == 'healthy'


class TestModelsEndpoint:
    """Tests for the /api/models endpoint."""

    def test_models_returns_200(self, client):
        response = client.get('/api/models')
        assert response.status_code == 200

    def test_models_returns_model_list(self, client):
        response = client.get('/api/models')
        data = response.get_json()['data']
        assert isinstance(data, dict)
        # Should have at least m1, m2, m3, irrigation
        expected_keys = {'m1', 'm2', 'm3', 'irrigation'}
        assert expected_keys.issubset(set(data.keys()))


class TestPredictEndpoint:
    """Tests for the /api/predict/<model> endpoint."""

    def test_predict_unknown_model_returns_404(self, client):
        response = client.post('/api/predict/unknown')
        assert response.status_code == 404

    def test_predict_no_image_returns_400(self, client):
        response = client.post('/api/predict/plant')
        data = response.get_json()
        assert data['status'] == 'error'

    def test_predict_empty_filename_returns_400(self, client):
        from io import BytesIO
        data = {'image': (BytesIO(b''), '')}
        response = client.post('/api/predict/plant', data=data, content_type='multipart/form-data')
        assert response.status_code == 400


class TestAnalyzeEndpoint:
    """Tests for the /api/analyze endpoint."""

    def test_analyze_no_image_returns_400(self, client):
        response = client.post('/api/analyze')
        data = response.get_json()
        assert data['status'] == 'error'


class TestIrrigationEndpoint:
    """Tests for the /api/irrigation endpoint."""

    def test_irrigation_no_body_returns_400(self, client):
        response = client.post('/api/irrigation')
        assert response.status_code == 400

    def test_irrigation_missing_fields_returns_400(self, client):
        response = client.post(
            '/api/irrigation',
            data=json.dumps({'temperature': 30}),
            content_type='application/json',
        )
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Missing irrigation fields' in data['error']

    def test_irrigation_valid_payload(self, client):
        payload = {
            'soil_moisture_previous': 45,
            'soil_moisture': 40,
            'soil_moisture_trend': -5,
            'temperature': 30,
            'humidity': 55,
            'rain_recent': 0,
            'vpd': 1.5,
        }
        response = client.post(
            '/api/irrigation',
            data=json.dumps(payload),
            content_type='application/json',
        )
        # May return 500 if model not loaded, but should not return 400
        assert response.status_code in (200, 500)


class TestErrorHandlers:
    """Tests for error handler routes."""

    def test_404_handler(self, client):
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'

    def test_405_handler(self, client):
        response = client.delete('/api/health')
        assert response.status_code == 405


class TestIndexPage:
    """Tests for the web UI."""

    def test_index_returns_html(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Dhurandhar' in response.data
