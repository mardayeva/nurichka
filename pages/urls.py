from django.urls import path

from .views import home_redirect, teachers_page, students_page

urlpatterns = [
    path("", home_redirect, name="home"),
    path("teachers/", teachers_page, name="teachers_page"),
    path("students/", students_page, name="students_page"),
]
