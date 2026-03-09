from django.urls import path
from .views import my_certificates

urlpatterns = [
    path("mine/", my_certificates, name="my_certificates"),
]