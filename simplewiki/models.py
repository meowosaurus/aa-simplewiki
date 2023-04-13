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
        permissions = (("basic_access", "Can access this app"),)

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
                            help_text='Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons.')
    name = models.CharField(max_length=255, 
                            unique=True,
                            help_text='The name of the URL. You will find that page under https://{your_auth_domain}/simplewiki/{name}.')

    def __str__(self):
        return self.name

class PageItem(models.Model):
    page_title = models.CharField(max_length=255, 
                                  null=True)
    menu_name = models.CharField(max_length=255, 
                                 unique=False,
                                 help_text='Menu under which this page should be displayed.')
    index = models.IntegerField(default=0, 
                                unique=True,
                                help_text='The entire wiki page is sorted by this index. The lower the value, the further to the top is the page.')
    icon = models.CharField(max_length=255, 
                            unique=False, 
                            null=True, 
                            blank=True,
                            help_text='Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons.')
    content = models.TextField(blank=True, 
                               null=True,
                               help_text='You can use HTML.')

    def __str__(self):
        return self.menu_name + ": " + self.page_title

