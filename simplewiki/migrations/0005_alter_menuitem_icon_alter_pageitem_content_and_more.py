# Generated by Django 4.0.10 on 2023-04-13 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simplewiki', '0004_pageitem_icon_alter_menuitem_icon_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='icon',
            field=models.CharField(blank=True, help_text='Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='pageitem',
            name='content',
            field=models.TextField(blank=True, help_text='You can use HTML.', null=True),
        ),
        migrations.AlterField(
            model_name='pageitem',
            name='icon',
            field=models.CharField(blank=True, help_text='Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='pageitem',
            name='index',
            field=models.IntegerField(default=0, help_text='The entire wiki page is sorted by this index. The lower the value, the further to the top is the page.', unique=True),
        ),
        migrations.AlterField(
            model_name='pageitem',
            name='menu_name',
            field=models.CharField(help_text='Menu under which this page should be displayed.', max_length=255),
        ),
    ]
