# Generated by Django 4.0.10 on 2024-02-10 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simplewiki', '0029_rename_last_edut_section_last_edit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='last_edit',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
