# 🎯 MediScan — Privacy-Preserving AI Model Platform

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-6.0.1-green.svg)](https://djangoproject.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.8.0-orange.svg)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MediScan is a secure, privacy-first web platform designed to execute machine learning models on sensitive health data without compromising user privacy. It addresses the critical issue of data leakage in AI deployments by enforcing strict local execution, cryptographic hashing, and comprehensive audit trails.

---

## 🚀 Key Features & Architectural Security

* **Secure Local Execution**: Runs a localized Scikit-Learn model (`.pkl`). The system performs inference completely offline with zero external API calls, protected by a `5-second` execution timeout to prevent resource-exhaustion DoS attacks.
* **Zero Raw Data Storage**: Biometric input fields (Age, BMI, Blood Pressure, Glucose, Cholesterol, Smoking status, Activity level) are **never saved** in the database. The system only stores a `SHA-256` cryptographic hash of the input signature alongside the final risk score.
* **Role-Based Access Control (RBAC)**: Users are kept in a pending status upon registration. An Administrator must review and approve their access via the Admin Panel before they can log in or perform inferences.
* **Immutable Audit Trail**: All authentication events (Logins, Logouts, Registration), approvals, access denials, and inference runs are written to an internal audit ledger tracking timestamps, client IP addresses, actions, and risk outcomes.

---

## 🎨 Premium UI/UX & Interactive Design

The frontend is crafted to look like a modern, state-of-the-art SaaS application using deep glassmorphism and animated accents:

* **Ambient Floating Orbs**: Smooth, slow-floating gradient blobs float in the background to add depth to the dark mode.
* **Dynamic Card Interactions**: Dashboard stats cards lift (`translate-y`) on hover and cast color-themed glow shadows matching their significance (emerald for latest runs, purple for averages, red for critical alerts).
* **Gradient Range Slider**: The Activity Level input is represented by a green-to-red gradient range slider accompanied by a live-syncing numeric badge.
* **Animated Risk Gauge**: On the results screen, an SVG circular gauge fills dynamically using a custom easing function while the numeric score counts up in tandem (e.g. from `0` to the target score) over 1.6 seconds.

---

## 💻 Tech Stack

* **Backend**: Django 6.0.1, Python 3
* **Machine Learning**: Scikit-Learn 1.8.0, NumPy, Joblib 1.5.3
* **Database**: SQLite (Highly optimized, zero setup required)
* **Frontend**: HTML5, TailwindCSS, Vanilla JavaScript (featuring custom CSS transitions and animations)

---

## ⚙️ Quick Start Guide

### 1. Install Dependencies
Make sure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Database Set Up & Migrations
The repository contains a pre-configured database, but you can re-run migrations at any point:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed Default Accounts
Generate pre-configured admin and approved test user credentials:
```bash
python seed.py
```

### 4. Start Development Server
```bash
python manage.py runserver
```
Visit the application locally at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔑 Default Test Credentials

| Role | Username | Password | Access Details |
|------|----------|----------|----------------|
| **Admin** | `admin` | `Admin@1234` | Full access to User Approvals & System Audit Logs. |
| **Test User** | `testuser` | `User@1234` | Pre-approved account to run health risk assessments. |

> [!IMPORTANT]
> Newly registered user accounts must be explicitly marked as **Approved** by the `admin` user via the **Admin Panel** before they can log in.

---

## 🧠 Machine Learning Model
The model is a tabular classifier trained to predict general health risk levels (Low, Medium, High, Critical) based on clinical thresholds.
* **Location**: `ml_models/risk_model.pkl`
* **Regeneration**: To retrain and export the classifier using synthetic health data, run:
  ```bash
  python ml_models/generate_model.py
  ```
* **Offline Tests**: You can verify model performance and raw predictions using the standalone pipeline script:
  ```bash
  python test_inference.py
  ```
