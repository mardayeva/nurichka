from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

from accounts.utils import student_required
from certificates.models import Certificate
from learning.models import ModuleProgress, Assignment, AssignmentSeen
from quizzes.models import Attempt

from .models import Course, Enrollment


@login_required
@student_required
def student_dashboard(request):
    my = Course.objects.filter(enrollments__student=request.user).order_by("-created_at")
    pending_assignments = (
        Assignment.objects.filter(course__in=my)
        .exclude(seen_rows__student=request.user)
        .exclude(submissions__student=request.user)
        .select_related("course")
        .order_by("-created_at")[:6]
    )
    stats = {
        "course_count": my.count(),
        "completed_modules": ModuleProgress.objects.filter(enrollment__student=request.user, is_completed=True).count(),
        "certificate_count": Certificate.objects.filter(student=request.user).count(),
        "pending_assignment_count": Assignment.objects.filter(course__in=my)
        .exclude(seen_rows__student=request.user)
        .exclude(submissions__student=request.user)
        .count(),
    }
    return render(
        request,
        "student/dashboard.html",
        {"courses": my, "stats": stats, "pending_assignments": pending_assignments},
    )


@login_required
@student_required
def join_course(request):
    msg = ""
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        code = request.POST.get("code", "").strip().upper()

        if first_name and last_name:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save(update_fields=["first_name", "last_name"])

        try:
            course = Course.objects.get(code=code)
            Enrollment.objects.create(course=course, student=request.user)
            return redirect("student_course_view", course_id=course.id)
        except Course.DoesNotExist:
            msg = "Bunday kod topilmadi."
        except IntegrityError:
            msg = "Siz allaqachon qo'shilgansiz."
    return render(request, "student/join_course.html", {"msg": msg})


@login_required
@student_required
def student_progress(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related("course").order_by("-joined_at")
    progress_rows = []
    for enr in enrollments:
        total_modules = enr.course.modules.count()
        completed_modules = ModuleProgress.objects.filter(enrollment=enr, is_completed=True).count()
        percent = round((completed_modules / total_modules) * 100) if total_modules else 0
        attempts = Attempt.objects.filter(quiz__module__course=enr.course, student=request.user)
        passed = attempts.filter(passed=True).count()
        progress_rows.append(
            {
                "course": enr.course,
                "completed_modules": completed_modules,
                "total_modules": total_modules,
                "percent": percent,
                "quiz_passed": passed,
                "quiz_total": attempts.count(),
            }
        )
    return render(request, "student/progress.html", {"rows": progress_rows})
