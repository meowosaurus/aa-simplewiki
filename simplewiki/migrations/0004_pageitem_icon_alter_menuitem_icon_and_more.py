# Generated by Django 4.0.10 on 2023-04-13 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simplewiki', '0003_menuitem_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageitem',
            name='icon',
            field=models.CharField(help_text='Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='icon',
            field=models.CharField(help_text='Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='index',
            field=models.IntegerField(default=0, help_text='The navbar is sorted by this index. The lower the value, the further to the left is the menu.', unique=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(help_text='The name of the URL. You will find that page under https://{your_auth_domain}/simplewiki/{name}.', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='title',
            field=models.CharField(help_text='The navbar title for the menu.', max_length=255, unique=True),
        ),
    ]
