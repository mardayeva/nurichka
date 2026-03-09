from django.urls import path
from .views_center import center_dashboard

urlpatterns = [
    path("", center_dashboard, name="center_dashboard"),
]
