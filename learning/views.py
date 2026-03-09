from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import re
from accounts.models import Profile
from accounts.utils import teacher_required, student_required
from courses.models import Course, Enrollment
from .models import Module, ModuleProgress, Assignment, AssignmentSubmission, AssignmentSeen
from .forms import ModuleForm, AssignmentForm, AssignmentSubmissionForm
from quizzes.models import Attempt
from certificates.services import issue_certificate_if_eligible

@login_required
@teacher_required
def module_create(request, course_id):
    course = Course.objects.filter(id=course_id, teacher=request.user).first()
    if not course:
        messages.error(request, "Bu kurs sizga tegishli emas yoki topilmadi.")
        return redirect("teacher_dashboard")
    if request.method == "POST":
        form = ModuleForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.cleaned_data["order"]
            if Module.objects.filter(course=course, order=order).exists():
                form.add_error("order", "Bu tartib raqami bu kursda allaqachon bor.")
                return render(request, "teacher/module_create.html", {"course": course, "form": form})
            m = form.save(commit=False)
            m.course = course
            try:
                m.save()
            except IntegrityError:
                form.add_error("order", "Bu tartib raqami bu kursda allaqachon bor.")
                return render(request, "teacher/module_create.html", {"course": course, "form": form})
            return redirect("teacher_course_detail", pk=course.id)
    else:
        form = ModuleForm()
    return render(request, "teacher/module_create.html", {"course": course, "form": form})

def _is_module_unlocked(enrollment: Enrollment, module: Module) -> bool:
    # 1-modul har doim ochiq
    if module.order == 1:
        return True
    prev = Module.objects.filter(course=module.course, order=module.order-1).first()
    if not prev:
        return True
    prev_prog = ModuleProgress.objects.filter(enrollment=enrollment, module=prev, is_completed=True).exists()
    # oldingi test passed bo‘lishi ham kerak (quiz bo‘lsa)
    prev_attempt_passed = True
    if hasattr(prev, "quiz"):
        prev_attempt_passed = Attempt.objects.filter(quiz=prev.quiz, student=enrollment.student, passed=True).exists()
    return prev_prog and prev_attempt_passed

@login_required
@student_required
def student_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
    if not enrollment:
        return redirect("student_dashboard")

    modules = course.modules.all()
    rows = {p.module_id: p for p in ModuleProgress.objects.filter(enrollment=enrollment)}
    module_cards = []
    for m in modules:
        unlocked = _is_module_unlocked(enrollment, m)
        prog = rows.get(m.id)
        module_cards.append({"m": m, "unlocked": unlocked, "done": bool(prog and prog.is_completed)})

    cert, ai_report = issue_certificate_if_eligible(course, request.user)
    teacher_profile, _ = Profile.objects.get_or_create(user=course.teacher, defaults={"role": "TEACHER"})
    return render(
        request,
        "student/course_view.html",
        {
            "course": course,
            "cards": module_cards,
            "teacher_profile": teacher_profile,
            "ai_report": ai_report,
            "certificate": cert,
        },
    )

@login_required
@student_required
def module_view(request, module_id):
    m = get_object_or_404(Module, id=module_id)
    enrollment = Enrollment.objects.filter(course=m.course, student=request.user).first()
    if not enrollment:
        return redirect("student_dashboard")

    if not _is_module_unlocked(enrollment, m):
        return redirect("student_course_view", course_id=m.course_id)

    prog, _ = ModuleProgress.objects.get_or_create(enrollment=enrollment, module=m)

    if request.method == "POST":
        prog.is_completed = True
        prog.completed_at = timezone.now()
        prog.save()
        # agar mavzuda quiz bo'lsa, studentni quizga yo'naltiramiz
        if hasattr(m, "quiz"):
            return redirect("quiz_take", quiz_id=m.quiz.id)
        return redirect("student_course_view", course_id=m.course_id)

    resource_links = [ln.strip() for ln in (m.resource_links or "").splitlines() if ln.strip()]
    image_ext = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
    image_links = [ln for ln in resource_links if ln.lower().endswith(image_ext)]
    doc_links = [ln for ln in resource_links if ln not in image_links]

    sections = []
    raw = (m.content or "").strip()
    if raw:
        lines = raw.splitlines()
        current_title = "Kirish"
        current_body = []
        for ln in lines:
            if ln.startswith("## "):
                if current_body:
                    sections.append({"title": current_title, "body": "\n".join(current_body).strip()})
                current_title = ln[3:].strip() or "Bo'lim"
                current_body = []
            else:
                current_body.append(ln)
        if current_body:
            sections.append({"title": current_title, "body": "\n".join(current_body).strip()})

        if not sections:
            sections = [{"title": "Mavzu matni", "body": raw}]

        used_ids = set()
        for s in sections:
            base = re.sub(r"[^a-z0-9]+", "-", s["title"].lower()).strip("-") or "bolim"
            sid = base
            i = 2
            while sid in used_ids:
                sid = f"{base}-{i}"
                i += 1
            used_ids.add(sid)
            s["id"] = sid

    module_image_url = None
    if m.resource_file and m.resource_file.name.lower().endswith(image_ext):
        module_image_url = m.resource_file.url

    return render(
        request,
        "student/module_view.html",
        {
            "module": m,
            "progress": prog,
            "sections": sections,
            "module_image_url": module_image_url,
            "image_links": image_links,
            "doc_links": doc_links,
        },
    )


@login_required
@teacher_required
def assignment_manage(request, course_id):
    course = Course.objects.filter(id=course_id, teacher=request.user).first()
    if not course:
        messages.error(request, "Bu kurs sizga tegishli emas yoki topilmadi.")
        return redirect("teacher_dashboard")

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.course = course
            obj.save()
            messages.success(request, "Topshiriq qo'shildi.")
            return redirect("assignment_manage", course_id=course.id)
    else:
        form = AssignmentForm()

    assignments = course.assignments.all()
    return render(
        request,
        "teacher/assignment_manage.html",
        {"course": course, "form": form, "assignments": assignments},
    )


@login_required
@teacher_required
def assignment_submissions(request, assignment_id):
    assignment = Assignment.objects.filter(id=assignment_id, course__teacher=request.user).first()
    if not assignment:
        messages.error(request, "Topshiriq topilmadi yoki sizga tegishli emas.")
        return redirect("teacher_dashboard")

    if request.method == "POST":
        sub_id = request.POST.get("submission_id")
        submission = AssignmentSubmission.objects.filter(id=sub_id, assignment=assignment).first()
        if submission:
            try:
                score = int(request.POST.get("score", "0"))
            except ValueError:
                score = 0
            submission.score = max(0, min(score, assignment.max_score))
            submission.feedback = request.POST.get("feedback", "").strip()
            submission.save(update_fields=["score", "feedback"])
            messages.success(request, "Baholash saqlandi.")
        return redirect("assignment_submissions", assignment_id=assignment.id)

    rows = assignment.submissions.select_related("student").all()
    return render(
        request,
        "teacher/assignment_submissions.html",
        {"assignment": assignment, "rows": rows},
    )


@login_required
@student_required
def student_assignments(request, course_id):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return redirect("student_dashboard")
    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
    if not enrollment:
        return redirect("student_dashboard")

    assignments = []
    for a in course.assignments.all():
        AssignmentSeen.objects.get_or_create(assignment=a, student=request.user)
        sub = AssignmentSubmission.objects.filter(assignment=a, student=request.user).first()
        assignments.append({"assignment": a, "submission": sub})

    return render(
        request,
        "student/assignments.html",
        {"course": course, "assignments": assignments},
    )


@login_required
@student_required
def assignment_submit(request, assignment_id):
    assignment = Assignment.objects.filter(id=assignment_id).first()
    if not assignment:
        return redirect("student_dashboard")
    enrollment = Enrollment.objects.filter(course=assignment.course, student=request.user).first()
    if not enrollment:
        return redirect("student_dashboard")

    submission, _ = AssignmentSubmission.objects.get_or_create(assignment=assignment, student=request.user)
    if request.method == "POST":
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Topshiriq yuborildi.")
            return redirect("student_assignments", course_id=assignment.course_id)
    else:
        form = AssignmentSubmissionForm(instance=submission)

    return render(
        request,
        "student/assignment_submit.html",
        {"assignment": assignment, "form": form, "submission": submission},
    )
