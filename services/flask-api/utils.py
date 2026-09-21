import time
from pathlib import Path
from PIL import Image
from flask import jsonify


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_image(file, max_size: int) -> Image.Image:
    try:
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > max_size:
            raise ValueError(f'File too large ({size} bytes). Maximum is {max_size} bytes.')
        image = Image.open(file)
        image.verify()
        file.seek(0)
        image = Image.open(file).convert('RGB')
        return image
    except Exception as exc:
        raise ValueError(f'Invalid image: {exc}') from exc


def success(data: dict, status=200):
    return jsonify({'status': 'success', 'timestamp': time.time(), 'data': data}), status


def error(message: str, status=400):
    return jsonify({'status': 'error', 'timestamp': time.time(), 'error': message}), status
