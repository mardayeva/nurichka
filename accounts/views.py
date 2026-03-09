from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import CustomAuthenticationForm, RegisterForm, ProfileForm
from .models import Profile


def register_view(request):
    """
    Register orqali user yaratadi va role (TEACHER/STUDENT) ni Profile ga yozadi,
    so'ng avtomatik login qilib panelga yuboradi.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # UserCreationForm userni yaratadi

            role = form.cleaned_data.get("role", "STUDENT")

            # Profile mavjud bo'lmasa ham yaratib yuboradi (signal bo'lsa ham xavfsiz)
            Profile.objects.update_or_create(
                user=user,
                defaults={"role": role}
            )

            login(request, user)
            messages.success(request, "Muvaffaqiyatli ro‘yxatdan o‘tdingiz!")
            return redirect("after_login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def after_login(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "STUDENT"},
    )
    role = profile.role

    if role == "TEACHER":
        return redirect("teacher_dashboard")
    if role == "CENTER_ADMIN":
        return redirect("center_dashboard")
    else:
        return redirect("student_dashboard")


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        return reverse("after_login")


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "STUDENT"},
    )
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil ma'lumotlari saqlandi.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile.html", {"form": form, "profile": profile})
