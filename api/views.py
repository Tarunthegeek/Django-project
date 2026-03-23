"""Views for authentication, dashboard rendering, and secure inference APIs."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from cryptography.fernet import InvalidToken
from rest_framework import parsers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from api.forms import CSVUploadForm, RegisterForm
from api.ml import batch_secure_inference, infer_from_plain_payload, secure_inference
from api.serializers import EncryptedPredictionSerializer, PredictionInputSerializer


class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'


class RegisterView(View):
    template_name = 'registration/register.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.is_staff = False
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful. You can now submit secure inference requests.')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'csv_form': CSVUploadForm(),
            'is_admin_user': request.user.is_staff,
        }
        return render(request, self.template_name, context)


class PredictAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle, BurstRateThrottle]

    def post(self, request, *args, **kwargs):
        try:
            if 'encrypted_payload' in request.data:
                serializer = EncryptedPredictionSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                result = secure_inference(serializer.validated_data['encrypted_payload'])
            else:
                serializer = PredictionInputSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                result = infer_from_plain_payload(serializer.validated_data)
        except (ValueError, InvalidToken) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class BatchPredictAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    throttle_classes = [UserRateThrottle, BurstRateThrottle]

    def post(self, request, *args, **kwargs):
        upload = request.FILES.get('csv_file')
        if upload is None:
            return Response({'detail': 'csv_file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            results = batch_secure_inference(upload.read())
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)
