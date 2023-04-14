"""
App Models
Create your models in here
"""

# Django
from django.db import models


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),
                       ("editor", "Can edit menues and sections"))

class MenuItem(models.Model):
    index = models.IntegerField(default=0, 
                                unique=True,
                                help_text='The navbar is sorted by this index. The lower the value, the further to the left is the menu.')
    title = models.CharField(max_length=255, 
                             unique=True,
                             help_text='The navbar title for the menu.')
    icon = models.CharField(max_length=255, 
                            unique=False, 
                            null=True, 
                            blank=True,
                            help_text='Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons. Format example: fas fa-hand-spock')
    path = models.CharField(max_length=255, 
                            unique=True,
                            null=True,
                            help_text='The path of the URL. You will find that page under https://{your_auth_domain}/simplewiki/{name}.')
    group = models.CharField(max_length=255, 
                             null=True,
                             blank=True,
                             help_text='Do you only want to show this page to one group of people? Insert the group name here and only they will be able to see the post and all of it\'s sections.')

    def __str__(self):
        return self.path

class SectionItem(models.Model):
    section_title = models.CharField(max_length=255, 
                                  null=True)
    menu_name = models.CharField(max_length=255, 
                                 unique=False,
                                 help_text='Menu under which this section should be displayed.')
    index = models.IntegerField(default=0, 
                                unique=True,
                                help_text='The entire wiki page is sorted by this index. The lower the value, the further to the top is the section.')
    icon = models.CharField(max_length=255, 
                            unique=False, 
                            null=True, 
                            blank=True,
                            help_text='Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons. Format example: fas fa-hand-spock')
    content = models.TextField(blank=True, 
                               null=True,
                               help_text='You can use HTML.')

    def __str__(self):
        return self.menu_name + ": " + self.section_title

