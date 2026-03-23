"""REST serializers for secure inference requests."""
from rest_framework import serializers


class PredictionInputSerializer(serializers.Serializer):
    study_hours = serializers.FloatField(min_value=0, max_value=24)
    attendance_rate = serializers.FloatField(min_value=0, max_value=100)
    previous_score = serializers.FloatField(min_value=0, max_value=100)
    student_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    contact_email = serializers.EmailField(required=False, allow_blank=True)


class EncryptedPredictionSerializer(serializers.Serializer):
    encrypted_payload = serializers.CharField()


class BatchPredictionRowSerializer(PredictionInputSerializer):
    pass
