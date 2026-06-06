import sys
import os
import django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediscan.settings')
django.setup()

from inference.pipeline import run_inference

test_cases = [
    {
        'name': 'Test Case 1: The Healthy Athlete',
        'data': {
            'age': 28, 'bmi': 22.5, 'blood_pressure': 115,
            'glucose': 85, 'cholesterol': 160, 'smoking': 0, 'activity_level': 9
        }
    },
    {
        'name': 'Test Case 2: The Stressed Office Worker',
        'data': {
            'age': 45, 'bmi': 28.5, 'blood_pressure': 135,
            'glucose': 105, 'cholesterol': 230, 'smoking': 0, 'activity_level': 3
        }
    },
    {
        'name': 'Test Case 3: The Synergy Danger Zone',
        'data': {
            'age': 58, 'bmi': 34.0, 'blood_pressure': 165,
            'glucose': 145, 'cholesterol': 280, 'smoking': 1, 'activity_level': 1
        }
    },
    {
        'name': 'Test Case 4: The Borderline Profile',
        'data': {
            'age': 40, 'bmi': 26.0, 'blood_pressure': 125,
            'glucose': 98, 'cholesterol': 210, 'smoking': 0, 'activity_level': 1
        }
    },
    {
        'name': 'Test Case 5: The Warning Signs Profile',
        'data': {
            'age': 50, 'bmi': 28.0, 'blood_pressure': 130,
            'glucose': 110, 'cholesterol': 220, 'smoking': 0, 'activity_level': 4
        }
    }
]

for tc in test_cases:
    print(f"\n{tc['name']}")
    print('-'*40)
    result = run_inference(tc['data'])
    if result['success']:
        print(f"Risk Score: {result['risk_score']} / 100")
        print(f"Risk Level: {result['risk_level'].upper()}")
        print(f"Top Factors: {', '.join(result['top_factors'])}")
    else:
        print(f"Error: {result['error']}")
