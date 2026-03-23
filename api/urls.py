from django.urls import path

from api.views import BatchPredictAPIView, PredictAPIView

urlpatterns = [
    path('predict/', PredictAPIView.as_view(), name='predict'),
    path('predict/batch/', BatchPredictAPIView.as_view(), name='batch-predict'),
]
