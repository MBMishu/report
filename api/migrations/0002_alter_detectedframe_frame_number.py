# Generated by Django 4.2.10 on 2024-02-08 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="detectedframe",
            name="frame_number",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]