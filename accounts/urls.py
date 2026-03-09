from django.urls import path
from .views import register_view, after_login, CustomLoginView, profile_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("after-login/", after_login, name="after_login"),
    path("profile/", profile_view, name="profile"),
]
