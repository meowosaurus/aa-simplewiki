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
    index = models.IntegerField(default=0, unique=True)
    title = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class PageItem(models.Model):
    page_title = models.CharField(max_length=255, null=True)
    menu_name = models.CharField(max_length=255, unique=False)
    index = models.IntegerField(default=0, unique=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.menu_name + ": " + self.page_title

