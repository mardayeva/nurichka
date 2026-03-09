from django.shortcuts import render

from accounts.models import Profile
from courses.models import Enrollment
from learning.models import ModuleProgress
from quizzes.models import Attempt


def home_redirect(request):
    stats = {
        "teacher_count": Profile.objects.filter(role="TEACHER").count(),
        "student_count": Profile.objects.filter(role="STUDENT").count(),
        "enrollment_count": Enrollment.objects.count(),
    }
    return render(request, "pages/home.html", {"stats": stats})


def teachers_page(request):
    teachers_qs = (
        Profile.objects.filter(role="TEACHER")
        .select_related("user", "center")
        .order_by("-experience_years", "user__username")
    )
    teachers = []
    for p in teachers_qs:
        teachers.append(
            {
                "name": p.full_name or p.user.get_full_name() or p.user.username,
                "specialization": p.specialization or "Yo'nalish ko'rsatilmagan",
                "center": p.center.name if p.center else (p.center_name or "Mustaqil o'qituvchi"),
                "exp": p.experience_years,
                "course_count": p.user.courses.count(),
            }
        )
    return render(request, "pages/teachers.html", {"teachers": teachers})


def students_page(request):
    student_rows = []
    enrollment_qs = Enrollment.objects.select_related("student", "course").order_by("-joined_at")[:120]
    by_student = {}
    for enr in enrollment_qs:
        by_student.setdefault(enr.student_id, {"student": enr.student, "enrollments": []})["enrollments"].append(enr)

    for row in by_student.values():
        student = row["student"]
        enrollments = row["enrollments"]
        total_modules = 0
        completed_modules = 0
        total_quiz = 0
        passed_quiz = 0
        for enr in enrollments:
            course_modules = enr.course.modules.count()
            total_modules += course_modules
            completed_modules += ModuleProgress.objects.filter(enrollment=enr, is_completed=True).count()
            attempts = Attempt.objects.filter(quiz__module__course=enr.course, student=student)
            total_quiz += attempts.count()
            passed_quiz += attempts.filter(passed=True).count()

        percent = round((completed_modules / total_modules) * 100) if total_modules else 0
        student_rows.append(
            {
                "name": student.get_full_name() or student.username,
                "course_count": len(enrollments),
                "completed_modules": completed_modules,
                "total_modules": total_modules,
                "passed_quiz": passed_quiz,
                "total_quiz": total_quiz,
                "percent": percent,
            }
        )

    student_rows.sort(key=lambda x: x["percent"], reverse=True)
    return render(request, "pages/students.html", {"students": student_rows})
