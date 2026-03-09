from django.urls import path
from .views_teacher import (
    teacher_dashboard,
    teacher_course_create,
    teacher_course_detail,
    teacher_course_students,
)

urlpatterns = [
    path("", teacher_dashboard, name="teacher_dashboard"),
    path("courses/new/", teacher_course_create, name="teacher_course_create"),
    path("courses/<int:pk>/", teacher_course_detail, name="teacher_course_detail"),
    path("courses/<int:pk>/students/", teacher_course_students, name="teacher_course_students"),
]
