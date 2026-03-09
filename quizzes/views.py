from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
import random
import re

from accounts.utils import student_required, teacher_required
from learning.models import Module

from .models import Attempt, Choice, Question, Quiz


STOPWORDS = {
    "va", "yoki", "uchun", "bilan", "ham", "bu", "shu", "qanday", "qaysi",
    "the", "and", "for", "with", "that", "from", "into", "your", "you",
}


def _normalize_sentences(text: str):
    chunks = re.split(r"[.!?\n]+", text or "")
    cleaned = []
    seen = set()
    for ch in chunks:
        s = re.sub(r"\s+", " ", ch).strip()
        if len(s) < 24:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(s)
    return cleaned


def _keyword_pool(sentences):
    words = []
    for s in sentences:
        for w in re.findall(r"[A-Za-zÀ-ÿ'\-]+", s):
            w2 = w.strip("-'").lower()
            if len(w2) >= 5 and w2 not in STOPWORDS:
                words.append(w2)
    uniq = []
    seen = set()
    for w in words:
        if w not in seen:
            seen.add(w)
            uniq.append(w)
    return uniq


def _build_cloze_question(sentence, pool):
    words = re.findall(r"[A-Za-zÀ-ÿ'\-]+", sentence)
    candidates = [w for w in words if len(w) >= 5 and w.lower() not in STOPWORDS]
    if not candidates:
        return None
    answer = max(candidates, key=len)
    pattern = re.compile(re.escape(answer), re.IGNORECASE)
    masked = pattern.sub("_____", sentence, count=1)
    q_text = f"Tushirib qoldirilgan so'zni toping: \"{masked}\""

    distractors = [w for w in pool if w.lower() != answer.lower()]
    random.shuffle(distractors)
    options = [answer] + distractors[:3]
    while len(options) < 4:
        options.append(f"{answer}{len(options)}")
    random.shuffle(options)
    correct_idx = options.index(answer)
    return q_text[:500], [o[:255] for o in options], correct_idx


def _auto_generate_questions(module, count=5):
    source = " ".join([module.title or "", module.content or "", module.resource_links or ""])
    sentences = _normalize_sentences(source)
    if not sentences:
        return []
    pool = _keyword_pool(sentences)
    random.shuffle(sentences)
    payloads = []
    for s in sentences:
        q = _build_cloze_question(s, pool)
        if q:
            payloads.append(q)
        if len(payloads) >= count:
            break
    return payloads


@login_required
@student_required
def quiz_take(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    qs = quiz.questions.prefetch_related("choices").all()

    if request.method == "POST":
        total = 0
        for q in qs:
            choice_id = request.POST.get(f"q_{q.id}")
            selected = Choice.objects.filter(id=choice_id, question=q).first()
            if selected and selected.is_correct:
                total += q.points

        attempt, _ = Attempt.objects.get_or_create(quiz=quiz, student=request.user)
        attempt.score = total
        attempt.passed = total >= quiz.module.passing_score
        attempt.save()
        return redirect("student_course_view", course_id=quiz.module.course_id)

    return render(request, "student/quiz_take.html", {"quiz": quiz, "questions": qs})


@login_required
@teacher_required
def quiz_create_for_module(request, module_id):
    m = Module.objects.filter(id=module_id, course__teacher=request.user).first()
    if not m:
        messages.error(request, "Mavzu topilmadi yoki sizga tegishli emas.")
        return redirect("teacher_dashboard")

    Quiz.objects.get_or_create(module=m, defaults={"title": f"{m.title} testi"})
    return redirect("quiz_manage_for_module", module_id=m.id)


@login_required
@teacher_required
def quiz_manage_for_module(request, module_id):
    m = Module.objects.filter(id=module_id, course__teacher=request.user).first()
    if not m:
        messages.error(request, "Mavzu topilmadi yoki sizga tegishli emas.")
        return redirect("teacher_dashboard")

    quiz, _ = Quiz.objects.get_or_create(module=m, defaults={"title": f"{m.title} testi"})

    if request.method == "POST":
        action = request.POST.get("action", "manual")
        if action == "auto_generate":
            try:
                auto_count = max(1, min(15, int(request.POST.get("auto_count", "5"))))
            except ValueError:
                auto_count = 5
            generated = _auto_generate_questions(m, count=auto_count)
            if not generated:
                messages.error(request, "Avtomatik test uchun mavzu matni yetarli emas. Avval content kiriting.")
                return redirect("quiz_manage_for_module", module_id=m.id)

            existing_texts = set(quiz.questions.values_list("text", flat=True))
            created = 0
            for q_text, options, correct_idx in generated:
                if q_text in existing_texts:
                    continue
                q = Question.objects.create(quiz=quiz, text=q_text, points=1)
                for i, opt in enumerate(options):
                    Choice.objects.create(question=q, text=opt, is_correct=(i == correct_idx))
                created += 1

            if created == 0:
                messages.warning(request, "Yangi savol yaratilmagan (avval yaratilgan savollar bilan bir xil).")
            else:
                messages.success(request, f"Avtomatik ravishda {created} ta savol yaratildi.")
            return redirect("quiz_manage_for_module", module_id=m.id)

        text = request.POST.get("text", "").strip()
        option_a = request.POST.get("option_a", "").strip()
        option_b = request.POST.get("option_b", "").strip()
        option_c = request.POST.get("option_c", "").strip()
        option_d = request.POST.get("option_d", "").strip()
        correct = request.POST.get("correct", "").strip()
        points_raw = request.POST.get("points", "1").strip()

        try:
            points = max(1, int(points_raw))
        except ValueError:
            points = 1

        if not text or not option_a or not option_b or not option_c or not option_d or correct not in {"A", "B", "C", "D"}:
            messages.error(request, "Savol, 4 ta variant va to'g'ri javobni to'liq kiriting.")
            return redirect("quiz_manage_for_module", module_id=m.id)

        q = Question.objects.create(quiz=quiz, text=text, points=points)
        Choice.objects.create(question=q, text=option_a, is_correct=(correct == "A"))
        Choice.objects.create(question=q, text=option_b, is_correct=(correct == "B"))
        Choice.objects.create(question=q, text=option_c, is_correct=(correct == "C"))
        Choice.objects.create(question=q, text=option_d, is_correct=(correct == "D"))

        messages.success(request, "Savol qo'shildi.")
        return redirect("quiz_manage_for_module", module_id=m.id)

    questions = quiz.questions.prefetch_related("choices").all()
    return render(
        request,
        "teacher/quiz_manage.html",
        {"module": m, "quiz": quiz, "questions": questions},
    )
