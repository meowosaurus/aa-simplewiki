# Generated by Django 4.0.10 on 2023-04-13 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simplewiki', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageitem',
            name='page_title',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
