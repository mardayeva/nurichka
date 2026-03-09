from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.utils import student_required
from .models import Certificate

@login_required
@student_required
def my_certificates(request):
    certs = Certificate.objects.filter(student=request.user).order_by("-issued_at")
    return render(request, "student/certificates.html", {"certs": certs})