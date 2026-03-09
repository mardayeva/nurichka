from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("certificates", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="certificate",
            name="max_score",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="certificate",
            name="percentage",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="certificate",
            name="total_score",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
