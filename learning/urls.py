from django.urls import path
from .views import (
    module_create,
    student_course_view,
    module_view,
    assignment_manage,
    assignment_submissions,
    student_assignments,
    assignment_submit,
)

urlpatterns = [
    path("teacher/course/<int:course_id>/modules/new/", module_create, name="module_create"),
    path("teacher/course/<int:course_id>/assignments/", assignment_manage, name="assignment_manage"),
    path("teacher/assignments/<int:assignment_id>/submissions/", assignment_submissions, name="assignment_submissions"),
    path("student/course/<int:course_id>/", student_course_view, name="student_course_view"),
    path("student/course/<int:course_id>/assignments/", student_assignments, name="student_assignments"),
    path("student/assignments/<int:assignment_id>/submit/", assignment_submit, name="assignment_submit"),
    path("student/module/<int:module_id>/", module_view, name="module_view"),
]
