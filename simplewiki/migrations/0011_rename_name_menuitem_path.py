# Generated by Django 4.0.10 on 2023-04-14 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplewiki', '0010_rename_path_menuitem_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='name',
            new_name='path',
        ),
    ]
