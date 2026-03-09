import random, string
from django.conf import settings
from django.db import models

def gen_code(n=7):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(n))

class Course(models.Model):
    center = models.ForeignKey("accounts.Center", on_delete=models.SET_NULL, null=True, blank=True, related_name="courses")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=10, unique=True, default=gen_code)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "student")
