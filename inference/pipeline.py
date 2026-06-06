"""
Inference pipeline — Privacy-Preserving ML Engine

Steps:
  1. Validate inputs
  2. Mask PII fields
  3. Hash inputs (SHA-256, never store raw)
  4. Load model securely (local path only)
  5. Run prediction with timeout protection
  6. Map score to risk level
  7. Return result with top contributing factors
"""
import hashlib
import json
import re
import concurrent.futures
from typing import Any

import joblib
import numpy as np
from django.conf import settings


# ─────────────────────────────────────────────
# PII MASKING
# ─────────────────────────────────────────────

def mask_email(email: str) -> str:
    """u***@***.com"""
    if not email or '@' not in email:
        return '***@***'
    local, domain = email.split('@', 1)
    masked_local = local[0] + '***' if local else '***'
    domain_parts = domain.split('.')
    masked_domain = '***.' + domain_parts[-1] if domain_parts else '***'
    return f"{masked_local}@{masked_domain}"


def mask_name(name: str) -> str:
    """John Doe → J*** D***"""
    if not name:
        return '***'
    parts = name.strip().split()
    return ' '.join(p[0] + '***' for p in parts if p)


def mask_pii(data: dict) -> dict:
    """Returns a copy of data with PII fields masked."""
    masked = dict(data)
    pii_fields = {
        'email': mask_email,
        'name': mask_name,
        'full_name': mask_name,
        'patient_name': mask_name,
    }
    for field, masker in pii_fields.items():
        if field in masked and masked[field]:
            masked[field] = masker(str(masked[field]))
    return masked


# ─────────────────────────────────────────────
# INPUT HASHING
# ─────────────────────────────────────────────

def hash_input(data: dict) -> str:
    """SHA-256 hash of the sorted, serialised input dict."""
    serialised = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialised.encode('utf-8')).hexdigest()


# ─────────────────────────────────────────────
# INPUT VALIDATION
# ─────────────────────────────────────────────

FEATURE_RANGES = {
    'age':             (1, 120),
    'bmi':             (10.0, 70.0),
    'blood_pressure':  (50, 250),
    'glucose':         (40, 500),
    'cholesterol':     (50, 600),
    'smoking':         (0, 1),      # binary
    'activity_level':  (0, 10),
}

FEATURE_LABELS = {
    'age':            'Age',
    'bmi':            'BMI',
    'blood_pressure': 'Blood Pressure',
    'glucose':        'Glucose Level',
    'cholesterol':    'Cholesterol',
    'smoking':        'Smoking Status',
    'activity_level': 'Activity Level',
}


def validate_inputs(data: dict) -> tuple[dict, list[str]]:
    """
    Returns (cleaned_data, errors).
    Errors is an empty list on success.
    """
    errors = []
    cleaned = {}

    for feature, (lo, hi) in FEATURE_RANGES.items():
        raw = data.get(feature)
        if raw is None or raw == '':
            errors.append(f"{FEATURE_LABELS[feature]} is required.")
            continue
        try:
            val = float(raw)
        except (TypeError, ValueError):
            errors.append(f"{FEATURE_LABELS[feature]} must be a number.")
            continue
        if not (lo <= val <= hi):
            errors.append(f"{FEATURE_LABELS[feature]} must be between {lo} and {hi}.")
            continue
        cleaned[feature] = val

    return cleaned, errors


# ─────────────────────────────────────────────
# MODEL LOADING (CACHED)
# ─────────────────────────────────────────────

_model_cache: Any = None


def load_model():
    """Load model from local path. Cached after first load."""
    global _model_cache
    if _model_cache is None:
        model_path = settings.ML_MODEL_PATH
        if not model_path.exists():
            raise FileNotFoundError(
                f"ML model not found at {model_path}. "
                "Run: py ml_models/generate_model.py"
            )
        _model_cache = joblib.load(model_path)
    return _model_cache


# ─────────────────────────────────────────────
# RISK SCORING
# ─────────────────────────────────────────────

def score_to_level(score: float) -> str:
    if score < 25:
        return 'low'
    elif score < 50:
        return 'medium'
    elif score < 75:
        return 'high'
    else:
        return 'critical'


def compute_top_factors(model, feature_values: list[float], top_n: int = 3) -> list[str]:
    """Return top N contributing features based on model importances × input magnitude."""
    feature_names = list(FEATURE_RANGES.keys())
    try:
        # The model is saved as a Pipeline
        if hasattr(model, 'named_steps'):
            classifier_step = list(model.named_steps.keys())[-1]
            clf = model.named_steps[classifier_step]
            # Logistic Regression uses coef_, Trees use feature_importances_
            if hasattr(clf, 'coef_'):
                importances = np.abs(clf.coef_[0])
            else:
                importances = clf.feature_importances_
        else:
            if hasattr(model, 'coef_'):
                importances = np.abs(model.coef_[0])
            else:
                importances = model.feature_importances_
    except (AttributeError, KeyError):
        # Fallback for models without feature_importances_
        return [FEATURE_LABELS[f] for f in feature_names[:top_n]]

    # Normalise input values to 0–1 range for weighting
    normed = []
    for i, (f, val) in enumerate(zip(feature_names, feature_values)):
        lo, hi = FEATURE_RANGES[f]
        normed.append((val - lo) / max(hi - lo, 1))

    scores = [imp * norm for imp, norm in zip(importances, normed)]
    ranked = sorted(
        zip(feature_names, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return [FEATURE_LABELS[name] for name, _ in ranked[:top_n]]


# ─────────────────────────────────────────────
# MAIN INFERENCE FUNCTION
# ─────────────────────────────────────────────

INFERENCE_TIMEOUT = 5  # seconds


def _run_model(model, feature_array):
    """Inner function executed in a thread with timeout."""
    proba = model.predict_proba(feature_array)[0]
    # Risk score: probability of positive class × 100
    return float(proba[1]) * 100


def run_inference(raw_input: dict) -> dict:
    """
    Full secure inference pipeline.

    Args:
        raw_input: dict of feature values from the form

    Returns:
        {
            'success': bool,
            'risk_score': float,
            'risk_level': str,
            'top_factors': list[str],
            'input_hash': str,
            'error': str | None
        }
    """
    # 1. Validate
    cleaned, errors = validate_inputs(raw_input)
    if errors:
        return {'success': False, 'error': ' | '.join(errors)}

    # 2. Hash (before masking — captures original values, but never store raw)
    input_hash = hash_input(cleaned)

    # 3. Mask PII (for logging/display only — we don't use masked data for inference)
    # (Health features here are numeric; masking is still applied for any name/email keys if present)
    masked_input = mask_pii(raw_input)  

    # 4. Load model
    try:
        model = load_model()
    except FileNotFoundError as e:
        return {'success': False, 'error': str(e)}

    # 5. Build feature vector (order must match training)
    feature_order = list(FEATURE_RANGES.keys())
    feature_values = [cleaned[f] for f in feature_order]
    feature_array = np.array(feature_values).reshape(1, -1)

    # 6. Run with timeout
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_model, model, feature_array)
            risk_score = future.result(timeout=INFERENCE_TIMEOUT)
    except concurrent.futures.TimeoutError:
        return {'success': False, 'error': 'Inference timed out. Please try again.'}
    except Exception as e:
        return {'success': False, 'error': f'Model error: {str(e)}'}

    # 7. Map score to level
    risk_level = score_to_level(risk_score)

    # 8. Top contributing factors
    top_factors = compute_top_factors(model, feature_values)

    return {
        'success': True,
        'risk_score': round(risk_score, 2),
        'risk_level': risk_level,
        'top_factors': top_factors,
        'input_hash': input_hash,
        'error': None,
    }
