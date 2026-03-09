from django.conf import settings
from django.db import models


class Center(models.Model):
    name = models.CharField(max_length=180, unique=True)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_center")
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    ROLE_CHOICES = (
        ("TEACHER", "Teacher"),
        ("STUDENT", "Student"),
        ("CENTER_ADMIN", "Center Admin"),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True, related_name="members")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="STUDENT")
    full_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    center_name = models.CharField(max_length=180, blank=True)
    specialization = models.CharField(max_length=160, blank=True)
    bio = models.TextField(blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        label = self.full_name or self.user.username
        return f"{label} ({self.role})"
