# Generated by Django 4.0.10 on 2024-02-10 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplewiki', '0028_section_last_edut'),
    ]

    operations = [
        migrations.RenameField(
            model_name='section',
            old_name='last_edut',
            new_name='last_edit',
        ),
    ]
