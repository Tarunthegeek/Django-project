"""Forms used by the HTML interface."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(help_text='Upload a CSV file with study_hours, attendance_rate, previous_score.')
