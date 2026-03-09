from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.utils import teacher_required
from learning.models import Module, ModuleProgress
from quizzes.models import Attempt

from .forms import CourseForm
from .models import Course, Enrollment


@login_required
@teacher_required
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user).order_by("-created_at")
    stats = {
        "course_count": courses.count(),
        "module_count": Module.objects.filter(course__teacher=request.user).count(),
        "student_count": Enrollment.objects.filter(course__teacher=request.user).values("student_id").distinct().count(),
    }
    return render(request, "teacher/dashboard.html", {"courses": courses, "stats": stats})


@login_required
@teacher_required
def teacher_course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.teacher = request.user
            c.center = getattr(request.user.profile, "center", None)
            c.save()
            return redirect("teacher_course_detail", pk=c.pk)
    else:
        form = CourseForm()
    return render(request, "teacher/course_create.html", {"form": form})


@login_required
@teacher_required
def teacher_course_detail(request, pk):
    course = Course.objects.filter(pk=pk, teacher=request.user).first()
    if not course:
        messages.error(request, "Bu kurs sizga tegishli emas yoki topilmadi.")
        return redirect("teacher_dashboard")
    modules = course.modules.all()
    return render(request, "teacher/course_detail.html", {"course": course, "modules": modules})


@login_required
@teacher_required
def teacher_course_students(request, pk):
    course = Course.objects.filter(pk=pk, teacher=request.user).first()
    if not course:
        messages.error(request, "Bu kurs sizga tegishli emas yoki topilmadi.")
        return redirect("teacher_dashboard")

    enrollments = Enrollment.objects.filter(course=course).select_related("student").order_by("-joined_at")
    total_modules = course.modules.count()
    rows = []
    for enr in enrollments:
        completed = ModuleProgress.objects.filter(enrollment=enr, is_completed=True).count()
        percent = round((completed / total_modules) * 100) if total_modules else 0
        attempts = Attempt.objects.filter(quiz__module__course=course, student=enr.student)
        passed = attempts.filter(passed=True).count()
        rows.append(
            {
                "student": enr.student,
                "joined_at": enr.joined_at,
                "completed": completed,
                "total_modules": total_modules,
                "percent": percent,
                "quiz_passed": passed,
                "quiz_total": attempts.count(),
            }
        )

    return render(
        request,
        "teacher/course_students.html",
        {"course": course, "rows": rows, "total_modules": total_modules},
    )
