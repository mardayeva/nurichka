from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import Center, Profile
from accounts.utils import center_admin_required
from courses.models import Course

User = get_user_model()


@login_required
@center_admin_required
def center_dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={"role": "CENTER_ADMIN"})
    center = getattr(request.user, "owned_center", None)
    if not center and profile.center_id:
        center = profile.center

    if request.method == "POST" and request.POST.get("action") == "create_center":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        if not name:
            messages.error(request, "Markaz nomini kiriting.")
            return redirect("center_dashboard")
        if center:
            messages.warning(request, "Sizda markaz allaqachon mavjud.")
            return redirect("center_dashboard")
        center = Center.objects.create(name=name, owner=request.user, phone=phone, address=address)
        profile.center = center
        profile.center_name = center.name
        profile.save(update_fields=["center", "center_name"])
        messages.success(request, "Markaz yaratildi.")
        return redirect("center_dashboard")

    if not center:
        return render(request, "center/dashboard.html", {"center": None})

    if request.method == "POST" and request.POST.get("action") == "assign_teacher":
        teacher_id = request.POST.get("teacher_id")
        teacher_profile = Profile.objects.filter(user_id=teacher_id, role="TEACHER").first()
        if not teacher_profile:
            messages.error(request, "O'qituvchi topilmadi.")
            return redirect("center_dashboard")
        teacher_profile.center = center
        teacher_profile.center_name = center.name
        teacher_profile.save(update_fields=["center", "center_name"])
        messages.success(request, "O'qituvchi markazga biriktirildi.")
        return redirect("center_dashboard")

    if request.method == "POST" and request.POST.get("action") == "assign_course_teacher":
        teacher_id = request.POST.get("teacher_id")
        course_id = request.POST.get("course_id")
        teacher_profile = Profile.objects.filter(user_id=teacher_id, role="TEACHER", center=center).first()
        course = Course.objects.filter(id=course_id, center=center).first()
        if not teacher_profile or not course:
            messages.error(request, "Teacher yoki kurs noto'g'ri.")
            return redirect("center_dashboard")
        course.teacher = teacher_profile.user
        course.save(update_fields=["teacher"])
        messages.success(request, "Kurs o'qituvchisi yangilandi.")
        return redirect("center_dashboard")

    if request.method == "POST" and request.POST.get("action") == "create_course":
        teacher_id = request.POST.get("teacher_id")
        title = request.POST.get("title", "").strip()
        subject = request.POST.get("subject", "").strip()
        description = request.POST.get("description", "").strip()
        teacher_profile = Profile.objects.filter(user_id=teacher_id, role="TEACHER", center=center).first()
        if not teacher_profile:
            messages.error(request, "Avval markazga biriktirilgan o'qituvchini tanlang.")
            return redirect("center_dashboard")
        if not title:
            messages.error(request, "Kurs nomi kerak.")
            return redirect("center_dashboard")
        Course.objects.create(
            center=center,
            teacher=teacher_profile.user,
            title=title,
            subject=subject,
            description=description,
        )
        messages.success(request, "Yangi kurs yaratildi.")
        return redirect("center_dashboard")

    teachers = Profile.objects.filter(role="TEACHER").select_related("user").order_by("user__username")
    center_teachers = teachers.filter(center=center)
    center_courses = Course.objects.filter(center=center).select_related("teacher").order_by("-created_at")
    stats = {
        "teacher_count": center_teachers.count(),
        "course_count": center_courses.count(),
        "student_count": center_courses.values("enrollments__student_id").distinct().count(),
    }
    return render(
        request,
        "center/dashboard.html",
        {
            "center": center,
            "teachers": teachers,
            "center_teachers": center_teachers,
            "center_courses": center_courses,
            "stats": stats,
        },
    )
