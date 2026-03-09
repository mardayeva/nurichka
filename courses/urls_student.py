from django.urls import path
from .views_student import student_dashboard, join_course, student_progress

urlpatterns = [
    path("", student_dashboard, name="student_dashboard"),
    path("join/", join_course, name="join_course"),
    path("progress/", student_progress, name="student_progress"),
]
