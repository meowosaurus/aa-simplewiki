"""
SimpleWiki Models

MenuItem model -> the nav menu bar entries
SectionItem model -> the sections that will appear under a menu
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
                       ("editor_access", "Can edit menues and sections"))

class MenuItem(models.Model):
    """
    Menu item model for wiki menu entries
    """

    # Menu items are sorted after this index
    index = models.IntegerField(default=0, 
                                unique=True,
                                help_text='Required: The navbar is sorted by this index. The lower the value, the further to the left is the menu.')
    # Public title for the menu
    title = models.CharField(max_length=255, 
                             unique=True,
                             help_text='Required: The navbar title for the menu.')
    # Icon next to the menu
    icon = models.CharField(max_length=255, 
                            unique=False, 
                            null=True, 
                            blank=True,
                            help_text='Optional: Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons. Format example: fas fa-hand-spock')
    # The url path of the menu, set automatically based on the title 
    path = models.CharField(max_length=255, 
                            unique=True,
                            null=True,
                            help_text='Required: The path of the URL. You will find that page under https://{your_auth_domain}/simplewiki/{name}.')
    # Parent menu window, blank means it's the parent menu
    parent = models.CharField(max_length=255,
                              null=True,
                              blank=True,
                              help_text='Optional: Write the path of the parent menu. If you want this menu to be the parent leave this field empty.')
    # Menu visibility is filter by these groups
    groups = models.CharField(max_length=255, 
                             null=True,
                             blank=True,
                             help_text='Optional: Do you only want to show this page to one group of people? Insert the group name here and only they will be able to see the post and all of it\'s sections.')

    def __str__(self):
        return self.path

class SectionItem(models.Model):
    """
    Section item model for wiki page sections
    """

    # Header title for the section
    title = models.CharField(max_length=255, 
                             null=True,
                             unique=True,
                             help_text='Required: This title will be displayed above the content.')
    # Linked menu under which the section should appear under
    menu_path = models.CharField(max_length=255, 
                                 unique=False,
                                 help_text='Required: Menu under which this section should be displayed.')
    # Sorting index
    index = models.IntegerField(default=0, 
                                unique=False,
                                help_text='Required: The entire wiki page is sorted by this index. The lower the value, the further to the top is the section.')
    # Icon next to the title
    icon = models.CharField(max_length=255, 
                            unique=False, 
                            null=True, 
                            blank=True,
                            help_text='Optional: Go to https://fontawesome.com/v5/search to find matching icons. We only support free icons. Format example: fas fa-hand-spock')
    # Markdown text, will be converted to html code by commonmark
    content = models.TextField(blank=True, 
                               null=True,
                               help_text='Optional: This will be displayed as your main content of the section. You can use markdown. See https://commonmark.org/help/ for references.')

    def __str__(self):
        return self.menu_path + ": " + self.title

