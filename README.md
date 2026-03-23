# Privacy-Preserving AI Model Deployment Platform

A full-stack Django application that allows authenticated users to submit sensitive student performance data for machine-learning inference without storing raw payloads in the database. The platform encrypts request data in memory, decrypts it only inside `secure_inference()`, throttles API access, and stores audit logs for accountability.

## Features

- User registration and login with Django Auth.
- Role distinction using Django's built-in staff/admin flag.
- Secure `/predict/` JSON inference endpoint using Django REST Framework.
- Batch `/predict/batch/` CSV upload endpoint.
- Logistic Regression model trained on a sample pass/fail dataset.
- Fernet encryption for transient payload protection.
- Audit logging middleware that stores user, endpoint, method, and status code only.
- Simple HTML/CSS/JavaScript frontend for login, registration, dashboard, and prediction workflows.
- CSRF protection and per-user DRF rate limiting.

## Project Structure

```
project/
├── api/
├── auditlogs/
├── project/
│   ├── models/
│   └── settings.py
├── security/
├── static/
├── templates/
├── train_model.py
└── db.sqlite3
```

## Local Setup

1. Create and activate a virtual environment.
2. Copy environment defaults if needed: `cp .env.example .env`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create an admin user: `python manage.py createsuperuser`
6. Train the ML model: `python train_model.py`
7. Start the development server: `python manage.py runserver`
8. Open `http://127.0.0.1:8000/`

## Example API Request

Authenticate with a logged-in Django session, then send JSON to `/predict/`:

```bash
curl -X POST http://127.0.0.1:8000/predict/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <csrf-token>" \
  -b "sessionid=<session-cookie>; csrftoken=<csrf-token>" \
  -d '{
    "study_hours": 6.5,
    "attendance_rate": 91.0,
    "previous_score": 84.0,
    "student_name": "Ada Lovelace",
    "contact_email": "ada@example.com"
  }'
```

### Example API Response

```json
{
  "prediction": "Likely Pass",
  "prediction_code": 1,
  "confidence": 0.9842,
  "masked_subject": {
    "student_name": "Ad**********",
    "contact_email": "a**@example.com"
  }
}
```

## Privacy Model

- The request body is validated and encrypted in memory.
- `secure_inference()` is the only place where data is decrypted.
- Raw request payloads are never written to the database.
- Audit logs store metadata only, not sensitive values.

## Notes

- If `project/models/model.pkl` does not exist, the application auto-trains the sample model on first inference.
- Use `examples/sample_predictions.csv` to test the batch upload endpoint quickly.
- To create an Admin user, mark `is_staff=True` via Django admin or `createsuperuser`.
