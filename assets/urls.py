from django.urls import path
from .views import (
  ReportApiView,
)

urlpatterns = [
  path('report', ReportApiView.as_view()),
]