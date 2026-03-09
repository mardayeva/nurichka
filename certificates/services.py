from django.core.files.base import ContentFile
from django.db.models import Sum
from django.utils import timezone

from courses.models import Enrollment
from learning.models import ModuleProgress, Assignment, AssignmentSubmission
from quizzes.models import Attempt, Question, Quiz

from .models import Certificate


def _new_cert_id():
    from uuid import uuid4

    return uuid4().hex[:12].upper()


def _build_certificate_svg(student_name, course_title, cert_id, percentage, total_score, max_score, issued_date):
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='1600' height='1100' viewBox='0 0 1600 1100'>
  <defs>
    <linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>
      <stop offset='0%' stop-color='#0b132b'/>
      <stop offset='100%' stop-color='#1c7c7d'/>
    </linearGradient>
    <linearGradient id='gold' x1='0' y1='0' x2='1' y2='1'>
      <stop offset='0%' stop-color='#f7d774'/>
      <stop offset='100%' stop-color='#d4a017'/>
    </linearGradient>
  </defs>
  <rect x='0' y='0' width='1600' height='1100' fill='url(#bg)'/>
  <rect x='50' y='50' width='1500' height='1000' rx='28' fill='none' stroke='url(#gold)' stroke-width='8'/>
  <rect x='75' y='75' width='1450' height='950' rx='20' fill='none' stroke='rgba(247,215,116,0.55)' stroke-width='2'/>
  <circle cx='130' cy='130' r='58' fill='none' stroke='rgba(255,255,255,0.25)'/>
  <circle cx='1470' cy='970' r='68' fill='none' stroke='rgba(255,255,255,0.25)'/>

  <text x='800' y='220' text-anchor='middle' fill='#f9d66c' font-family='Georgia, serif' font-size='78' font-weight='700'>SERTIFIKAT</text>
  <text x='800' y='285' text-anchor='middle' fill='#d8e6ff' font-family='Arial, sans-serif' font-size='34'>Kursni muvaffaqiyatli yakunlagani uchun</text>

  <text x='800' y='390' text-anchor='middle' fill='#c9d7ef' font-family='Arial, sans-serif' font-size='28'>Ushbu sertifikat taqdim etiladi:</text>
  <text x='800' y='470' text-anchor='middle' fill='#ffffff' font-family='Georgia, serif' font-size='62' font-weight='700'>{student_name}</text>

  <text x='800' y='555' text-anchor='middle' fill='#c9d7ef' font-family='Arial, sans-serif' font-size='28'>Quyidagi kurs bo'yicha:</text>
  <text x='800' y='625' text-anchor='middle' fill='#ffffff' font-family='Arial, sans-serif' font-size='46' font-weight='700'>{course_title}</text>

  <text x='800' y='710' text-anchor='middle' fill='#f9d66c' font-family='Arial, sans-serif' font-size='34' font-weight='700'>Natija: {percentage}% ({total_score}/{max_score} ball)</text>

  <circle cx='1140' cy='830' r='108' fill='none' stroke='url(#gold)' stroke-width='6'/>
  <circle cx='1140' cy='830' r='86' fill='none' stroke='rgba(247,215,116,0.75)' stroke-width='2'/>
  <text x='1140' y='820' text-anchor='middle' fill='#f9d66c' font-family='Arial, sans-serif' font-size='20' font-weight='700'>NURICHKA</text>
  <text x='1140' y='848' text-anchor='middle' fill='#e9f2ff' font-family='Arial, sans-serif' font-size='17'>O'QUV MARKAZI</text>

  <line x1='220' y1='940' x2='720' y2='940' stroke='rgba(255,255,255,0.55)' stroke-width='2'/>
  <text x='470' y='928' text-anchor='middle' fill='#f8e9be' font-family='Brush Script MT, cursive' font-size='46'>D. Mardayeva</text>

  <text x='94' y='1020' fill='#dbe8ff' font-family='Arial, sans-serif' font-size='21'>Berilgan sana: {issued_date}</text>
  <text x='1140' y='1020' fill='#dbe8ff' font-family='Arial, sans-serif' font-size='21'>Sertifikat ID: {cert_id}</text>
</svg>""".encode("utf-8")


def evaluate_course_mastery(course, student):
    enrollment = Enrollment.objects.filter(course=course, student=student).first()
    if not enrollment:
        return {"eligible": False, "reason": "Kursga qo'shilmagan."}

    modules = course.modules.all()
    total_modules = modules.count()
    if total_modules == 0:
        return {"eligible": False, "reason": "Kursda mavzu yo'q."}

    completed_modules = ModuleProgress.objects.filter(enrollment=enrollment, is_completed=True).count()

    quizzes = Quiz.objects.filter(module__course=course)
    total_quizzes = quizzes.count()
    assignments = Assignment.objects.filter(course=course)
    total_assignments = assignments.count()
    submitted_assignments = AssignmentSubmission.objects.filter(
        assignment__in=assignments, student=student
    ).count()
    assignment_max_score = assignments.aggregate(s=Sum("max_score"))["s"] or 0
    assignment_total_score = (
        AssignmentSubmission.objects.filter(
            assignment__in=assignments,
            student=student,
            score__isnull=False,
        ).aggregate(s=Sum("score"))["s"]
        or 0
    )

    if total_quizzes < total_modules:
        assignment_percent = round((assignment_total_score / assignment_max_score) * 100) if assignment_max_score else 0
        return {
            "eligible": False,
            "reason": "Sertifikat uchun har bir mavzuda test bo'lishi kerak.",
            "completed_modules": completed_modules,
            "total_modules": total_modules,
            "submitted_assignments": submitted_assignments,
            "total_assignments": total_assignments,
            "quiz_total_score": 0,
            "quiz_max_score": 0,
            "assignment_total_score": assignment_total_score,
            "assignment_max_score": assignment_max_score,
            "total_score": assignment_percent,
            "max_score": 100,
            "percentage": assignment_percent,
            "solved_quizzes": 0,
            "total_quizzes": total_quizzes,
        }

    attempts = Attempt.objects.filter(quiz__in=quizzes, student=student)
    solved_quizzes = attempts.count()

    quiz_max_score = Question.objects.filter(quiz__in=quizzes).aggregate(s=Sum("points"))["s"] or 0
    quiz_total_score = attempts.aggregate(s=Sum("score"))["s"] or 0

    raw_max_score = quiz_max_score + assignment_max_score
    raw_total_score = quiz_total_score + assignment_total_score
    percentage = round((raw_total_score / raw_max_score) * 100) if raw_max_score else 0

    all_modules_completed = completed_modules == total_modules
    all_tests_solved = solved_quizzes == total_quizzes
    minimum_percent = 70
    eligible = all_modules_completed and all_tests_solved and percentage >= minimum_percent

    if not all_modules_completed:
        reason = "Avval barcha mavzularni tugating."
    elif not all_tests_solved:
        reason = "Sertifikat uchun barcha mavzu testlarini yeching."
    elif percentage < minimum_percent:
        reason = f"Jami ball kam. Kamida {minimum_percent}% kerak."
    else:
        reason = "Sertifikat olish mumkin."

    return {
        "eligible": eligible,
        "reason": reason,
        "completed_modules": completed_modules,
        "total_modules": total_modules,
        "solved_quizzes": solved_quizzes,
        "total_quizzes": total_quizzes,
        "submitted_assignments": submitted_assignments,
        "total_assignments": total_assignments,
        "quiz_total_score": quiz_total_score,
        "quiz_max_score": quiz_max_score,
        "assignment_total_score": assignment_total_score,
        "assignment_max_score": assignment_max_score,
        "raw_total_score": raw_total_score,
        "raw_max_score": raw_max_score,
        "total_score": percentage,
        "max_score": 100,
        "percentage": percentage,
        "minimum_percent": minimum_percent,
    }


def issue_certificate_if_eligible(course, student):
    existing = Certificate.objects.filter(course=course, student=student).first()
    if existing:
        report = evaluate_course_mastery(course, student)
        report["percentage"] = report.get("percentage", existing.percentage or 0)
        report["total_score"] = report.get("total_score", existing.total_score or 0)
        report["max_score"] = report.get("max_score", existing.max_score or 100)
        report["eligible"] = True

        student_name = (student.get_full_name() or student.username).strip()
        issued_date = existing.issued_at.strftime("%Y-%m-%d")
        svg_bytes = _build_certificate_svg(
            student_name=student_name,
            course_title=course.title,
            cert_id=existing.certificate_id,
            percentage=report["percentage"],
            total_score=report["total_score"],
            max_score=report["max_score"],
            issued_date=issued_date,
        )
        filename = f"cert-{existing.certificate_id}.svg"
        existing.total_score = report["total_score"]
        existing.max_score = report["max_score"]
        existing.percentage = report["percentage"]
        existing.file.save(filename, ContentFile(svg_bytes, name=filename), save=False)
        existing.save(update_fields=["total_score", "max_score", "percentage", "file"])

        return existing, report

    report = evaluate_course_mastery(course, student)
    if not report["eligible"]:
        return None, report

    cert_id = _new_cert_id()
    student_name = (student.get_full_name() or student.username).strip()
    issued_date = timezone.now().strftime("%Y-%m-%d")
    svg_bytes = _build_certificate_svg(
        student_name=student_name,
        course_title=course.title,
        cert_id=cert_id,
        percentage=report["percentage"],
        total_score=report["total_score"],
        max_score=report["max_score"],
        issued_date=issued_date,
    )

    cert = Certificate.objects.create(
        course=course,
        student=student,
        certificate_id=cert_id,
        total_score=report["total_score"],
        max_score=report["max_score"],
        percentage=report["percentage"],
    )
    filename = f"cert-{cert_id}.svg"
    cert.file.save(filename, ContentFile(svg_bytes, name=filename), save=True)
    return cert, report
