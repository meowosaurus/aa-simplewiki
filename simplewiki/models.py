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

# v2

class Menu(models.Model):
    """
    Represents a menu item in the SimpleWiki application.

    Attributes:
        index (int): The index of the menu item.
        title (str): The title of the menu item.
        icon (str): The icon of the menu item.
        path (str): The path of the menu item.
        parent (Menu): The parent menu item, if any.
        groups (str): The groups that have access to the menu item.
        states (str): The states in which the menu item is visible.
    """
    index = models.IntegerField(default=0,
                                unique=False,
                                null=False)
    title = models.CharField(max_length=255,
                             unique=False,
                             null=False)
    icon = models.CharField(max_length=255,
                            unique=False,
                            null=False,
                            blank=True)
    path = models.CharField(max_length=255,
                            unique=True,
                            null=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children',
        null=True,
        blank=True
    )
    groups = models.CharField(max_length=255,
                              null=False,
                              blank=True)
    states = models.CharField(max_length=255,
                              null=False,
                              blank=True)

    def __str__(self):
        if self.parent:
            return self.title + " (Parent: " + self.parent.title + ")" 
        else:
            return self.title

class Section(models.Model):
    """
    Represents a section in the SimpleWiki application.

    A section is a container for content that is organized under a title and an optional menu.
    """

    title = models.CharField(max_length=255,
                             null=False,
                             blank=False,
                             unique=True)
    menu = models.ForeignKey(
                             Menu,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)
    index = models.IntegerField(default=0,
                                null=False,
                                blank=True,
                                unique=False)
    icon = models.CharField(max_length=255,
                            unique=False,
                            null=False,
                            blank=True)
    content = models.TextField(null=False,
                               blank=True)
    # editor's charcter name
    last_edit = models.CharField(max_length=255,
                                 null=False,
                                 blank=True)
    # edited on (date only)
    last_edit_date = models.DateField(auto_now=True, 
                                      null=False, 
                                      blank=True)
    # editor's character id
    last_edit_id = models.IntegerField(default=0,
                                       null=False,
                                       blank=True,
                                       unique=False)

    def __str__(self):
        if self.menu:
            return self.title + " (" + self.menu.title + ")"
        else:
            return self.title

# v1
# TODO: Will be removed in a later version, used for now to store old data

class MenuItem(models.Model):
    """
    Menu item model for wiki menu entries
    """

    # Menu items are sorted after this index
    index = models.IntegerField(default=0, 
                                unique=False,
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
    # Menu visibility is filter by these states
    states = models.CharField(max_length=255, 
                             null=True,
                             blank=True,
                             help_text='Optional: Do you only want to show this page to one state? Insert the state name here and only they will be able to see the post and all of it\'s sections.')

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

