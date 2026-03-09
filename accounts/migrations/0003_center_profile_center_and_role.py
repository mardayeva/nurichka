from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_profile_details"),
    ]

    operations = [
        migrations.CreateModel(
            name="Center",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180, unique=True)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("address", models.CharField(blank=True, max_length=220)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.OneToOneField(on_delete=models.CASCADE, related_name="owned_center", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name="profile",
            name="center",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name="members", to="accounts.center"),
        ),
        migrations.AlterField(
            model_name="profile",
            name="role",
            field=models.CharField(choices=[("TEACHER", "Teacher"), ("STUDENT", "Student"), ("CENTER_ADMIN", "Center Admin")], default="STUDENT", max_length=20),
        ),
    ]
