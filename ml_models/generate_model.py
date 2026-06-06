"""
MediScan ML Model Generator
Run once: py ml_models/generate_model.py

Trains a GradientBoostingClassifier on synthetic health data
and saves it as risk_model.pkl (never exposed via URL).

Features:
  age, bmi, blood_pressure, glucose, cholesterol, smoking, activity_level

Label: at_risk (1) or not_at_risk (0)
"""
import sys
import os

# Allow running from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import joblib
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score

# ─────────────────────────────────────────────
# Synthetic data generation
# ─────────────────────────────────────────────
rng = np.random.default_rng(seed=42)
N = 5000

age           = rng.integers(18, 90,  size=N).astype(float)
bmi           = rng.uniform(15, 55,   size=N)
blood_pressure= rng.integers(70, 200, size=N).astype(float)
glucose       = rng.integers(60, 400, size=N).astype(float)
cholesterol   = rng.integers(100, 500,size=N).astype(float)
smoking       = rng.integers(0, 2,    size=N).astype(float)   # 0 or 1
activity_level= rng.integers(0, 11,   size=N).astype(float)   # 0–10

X = np.column_stack([
    age, bmi, blood_pressure, glucose, cholesterol, smoking, activity_level
])

# ─────────────────────────────────────────────
# Medical Risk Logic (Based on clinical thresholds)
# ─────────────────────────────────────────────

# 1. Base risk naturally increases with age
base_risk = (age / 100) * 0.2 

# 2. Non-linear BMI risk (U-shape curve: underweight is bad, normal is good, obese is worse)
bmi_risk = np.where(bmi < 18.5, 0.1, np.where(bmi <= 25, 0.0, np.where(bmi < 30, 0.15, 0.3)))

# 3. Blood pressure risk (Normal < 120, Prehypertension < 140, Hypertension >= 140)
bp_risk = np.where(blood_pressure < 120, 0.0, np.where(blood_pressure < 140, 0.1, 0.25))

# 4. Glucose risk (Normal < 100, Prediabetes <= 125, Diabetes > 125)
glucose_risk = np.where(glucose < 100, 0.0, np.where(glucose <= 125, 0.1, 0.3))

# 5. Cholesterol risk (Normal < 200, Borderline < 240, High >= 240)
chol_risk = np.where(cholesterol < 200, 0.0, np.where(cholesterol < 240, 0.1, 0.2))

# 6. Smoking and Synergy (Smoking is bad, but smoking while over 50 compounds the cardiovascular risk)
smoking_risk = smoking * 0.15
synergy_risk = np.where((smoking == 1) & (age > 50), 0.2, 0.0)

# 7. Physical activity actively protects the cardiovascular system
activity_protection = (activity_level / 10) * 0.15

# Total accumulated clinical risk points
risk_score = (
    base_risk + bmi_risk + bp_risk + glucose_risk + 
    chol_risk + smoking_risk + synergy_risk - activity_protection
)

# Convert raw risk points into a smooth probability curve (Logistic function)
# A risk score of 0.45 is the clinical threshold for 50% probability of severe risk
logit = (risk_score - 0.45) * 15
true_probability = 1 / (1 + np.exp(-logit))

# Sample the binary label using the true probability 
y = rng.binomial(1, true_probability)

print(f"Dataset: {N} samples | at-risk: {y.sum()} ({y.mean()*100:.1f}%)")

# ─────────────────────────────────────────────
# Train / test split
# ─────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ─────────────────────────────────────────────
# Model pipeline
# ─────────────────────────────────────────────
# We use Logistic Regression for smooth, mathematically calibrated probabilities
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, C=0.5))
])

pipeline.fit(X_train, y_train)

# ─────────────────────────────────────────────
# Evaluation
# ─────────────────────────────────────────────
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_proba)

print("\n=== Model Evaluation ===")
print(classification_report(y_test, y_pred, target_names=['Not at Risk', 'At Risk']))
print(f"ROC-AUC: {auc:.4f}")

# ─────────────────────────────────────────────
# Save model
# ─────────────────────────────────────────────
output_path = Path(__file__).parent / 'risk_model.pkl'
joblib.dump(pipeline, output_path)
print(f"\n[OK] Model saved -> {output_path}")
print(f"     File size: {output_path.stat().st_size / 1024:.1f} KB")
