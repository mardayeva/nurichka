from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0002_module_resource_file_module_resource_links"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=220)),
                ("description", models.TextField()),
                ("due_date", models.DateTimeField(blank=True, null=True)),
                ("max_score", models.PositiveIntegerField(default=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("course", models.ForeignKey(on_delete=models.CASCADE, related_name="assignments", to="courses.course")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="AssignmentSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text_answer", models.TextField(blank=True)),
                ("file", models.FileField(blank=True, null=True, upload_to="assignment_submissions/")),
                ("submitted_at", models.DateTimeField(auto_now=True)),
                ("score", models.PositiveIntegerField(blank=True, null=True)),
                ("feedback", models.TextField(blank=True)),
                ("assignment", models.ForeignKey(on_delete=models.CASCADE, related_name="submissions", to="learning.assignment")),
                ("student", models.ForeignKey(on_delete=models.CASCADE, related_name="assignment_submissions", to="auth.user")),
            ],
            options={"ordering": ["-submitted_at"], "unique_together": {("assignment", "student")}},
        ),
    ]
