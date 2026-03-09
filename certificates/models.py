from django.conf import settings
from django.db import models
from courses.models import Course

class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates")
    certificate_id = models.CharField(max_length=32, unique=True)
    total_score = models.PositiveIntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    percentage = models.PositiveIntegerField(default=0)
    issued_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="certificates/", null=True, blank=True)

    class Meta:
        unique_together = ("course", "student")
