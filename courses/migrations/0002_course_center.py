from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_center_profile_center_and_role"),
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="center",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name="courses", to="accounts.center"),
        ),
    ]
