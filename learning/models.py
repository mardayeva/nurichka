from django.db import models
from courses.models import Course, Enrollment

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    video_url = models.URLField(blank=True)      # YouTube link
    content = models.TextField(blank=True)       # matn
    resource_file = models.FileField(upload_to="module_resources/", blank=True, null=True)
    resource_links = models.TextField(blank=True)  # har qatorga bitta link

    passing_score = models.PositiveIntegerField(default=1)  # mavzu testidan o'tish uchun minimal

    class Meta:
        unique_together = ("course", "order")
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} / {self.order}. {self.title}"

class ModuleProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="progress")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="progress_rows")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("enrollment", "module")


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=220)
    description = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    max_score = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="assignment_submissions")
    text_answer = models.TextField(blank=True)
    file = models.FileField(upload_to="assignment_submissions/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ("assignment", "student")
        ordering = ["-submitted_at"]


class AssignmentSeen(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="seen_rows")
    student = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="assignment_seen_rows")
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assignment", "student")
        ordering = ["-seen_at"]
