"""Forms for inference input."""
from django import forms


class InferenceInputForm(forms.Form):
    age = forms.IntegerField(
        min_value=1, max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 45',
            'id': 'id_age',
        }),
        label='Age (years)',
        help_text='Patient age in years (1–120)'
    )
    bmi = forms.FloatField(
        min_value=10.0, max_value=70.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 24.5',
            'step': '0.1',
            'id': 'id_bmi',
        }),
        label='BMI',
        help_text='Body Mass Index (10–70)'
    )
    blood_pressure = forms.IntegerField(
        min_value=50, max_value=250,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 120',
            'id': 'id_blood_pressure',
        }),
        label='Blood Pressure (mmHg)',
        help_text='Systolic blood pressure (50–250 mmHg)'
    )
    glucose = forms.IntegerField(
        min_value=40, max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 95',
            'id': 'id_glucose',
        }),
        label='Glucose Level (mg/dL)',
        help_text='Fasting glucose (40–500 mg/dL)'
    )
    cholesterol = forms.IntegerField(
        min_value=50, max_value=600,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. 200',
            'id': 'id_cholesterol',
        }),
        label='Cholesterol (mg/dL)',
        help_text='Total cholesterol (50–600 mg/dL)'
    )
    smoking = forms.ChoiceField(
        choices=[('0', 'Non-Smoker'), ('1', 'Smoker')],
        widget=forms.Select(attrs={
            'class': 'form-input',
            'id': 'id_smoking',
        }),
        label='Smoking Status',
    )
    activity_level = forms.IntegerField(
        min_value=0, max_value=10,
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '0',
            'max': '10',
            'step': '1',
            'class': 'form-input',
            'id': 'id_activity_level',
        }),
        label='Activity Level (0–10)',
        help_text='Physical activity score: 0 = sedentary, 10 = very active'
    )
