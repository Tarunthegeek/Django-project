"""Secure machine-learning inference utilities."""
from __future__ import annotations

import csv
import io
import random
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
from django.conf import settings
from sklearn.linear_model import LogisticRegression

from security.crypto import decrypt_payload, encrypt_payload
from security.masking import mask_email, mask_value

FEATURE_ORDER = ['study_hours', 'attendance_rate', 'previous_score']
MODEL_DIR = Path(settings.MODEL_ARTIFACT_PATH).parent


def train_and_save_model() -> Path:
    """Train a simple logistic regression classifier and persist it to disk."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    random.seed(42)
    X: list[list[float]] = []
    y: list[int] = []
    for _ in range(400):
        study_hours = round(random.uniform(0.5, 10.0), 2)
        attendance_rate = round(random.uniform(40.0, 100.0), 2)
        previous_score = round(random.uniform(25.0, 100.0), 2)
        risk_score = (study_hours * 8.0) + (attendance_rate * 0.35) + (previous_score * 0.45)
        passed = int(risk_score >= 75)
        X.append([study_hours, attendance_rate, previous_score])
        y.append(passed)

    model = LogisticRegression(max_iter=500, random_state=42)
    model.fit(X, y)
    artifact = {
        'model': model,
        'features': FEATURE_ORDER,
        'labels': {0: 'At Risk', 1: 'Likely Pass'},
    }
    joblib.dump(artifact, settings.MODEL_ARTIFACT_PATH)
    return Path(settings.MODEL_ARTIFACT_PATH)


def ensure_model_artifact() -> Path:
    artifact_path = Path(settings.MODEL_ARTIFACT_PATH)
    if not artifact_path.exists():
        return train_and_save_model()
    return artifact_path


@lru_cache(maxsize=1)
def load_model_artifact() -> dict[str, Any]:
    ensure_model_artifact()
    return joblib.load(settings.MODEL_ARTIFACT_PATH)


def sanitize_payload(data: dict[str, Any]) -> dict[str, Any]:
    sanitized = {
        'study_hours': round(float(data['study_hours']), 2),
        'attendance_rate': round(float(data['attendance_rate']), 2),
        'previous_score': round(float(data['previous_score']), 2),
        'student_name': str(data.get('student_name', '')).strip()[:120],
        'contact_email': str(data.get('contact_email', '')).strip()[:254],
    }

    if not 0 <= sanitized['study_hours'] <= 24:
        raise ValueError('study_hours must be between 0 and 24.')
    if not 0 <= sanitized['attendance_rate'] <= 100:
        raise ValueError('attendance_rate must be between 0 and 100.')
    if not 0 <= sanitized['previous_score'] <= 100:
        raise ValueError('previous_score must be between 0 and 100.')

    return sanitized


def secure_inference(encrypted_payload: str) -> dict[str, Any]:
    """Decrypt, sanitize, infer, and return prediction data without persisting raw inputs."""
    decrypted = decrypt_payload(encrypted_payload)
    sanitized = sanitize_payload(decrypted)
    artifact = load_model_artifact()
    model = artifact['model']
    features = [[sanitized[field] for field in FEATURE_ORDER]]
    prediction = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]
    confidence = float(max(probabilities))
    label = artifact['labels'][prediction]

    return {
        'prediction': label,
        'prediction_code': prediction,
        'confidence': round(confidence, 4),
        'masked_subject': {
            'student_name': mask_value(sanitized.get('student_name', ''), keep=2),
            'contact_email': mask_email(sanitized.get('contact_email', '')),
        },
    }


def infer_from_plain_payload(data: dict[str, Any]) -> dict[str, Any]:
    sanitized = sanitize_payload(data)
    encrypted_payload = encrypt_payload(sanitized)
    return secure_inference(encrypted_payload)


def batch_secure_inference(file_bytes: bytes) -> list[dict[str, Any]]:
    decoded = file_bytes.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    required = set(FEATURE_ORDER)
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValueError('CSV must contain study_hours, attendance_rate, and previous_score columns.')

    results: list[dict[str, Any]] = []
    for index, row in enumerate(reader, start=1):
        payload = {
            'study_hours': row.get('study_hours', 0),
            'attendance_rate': row.get('attendance_rate', 0),
            'previous_score': row.get('previous_score', 0),
            'student_name': row.get('student_name', ''),
            'contact_email': row.get('contact_email', ''),
        }
        prediction = infer_from_plain_payload(payload)
        prediction['row'] = index
        results.append(prediction)
    return results
