from django.core.management.base import BaseCommand
from django.db.models import Q

from simplewiki.models import *

# Command to migrate data from 1.0.x to 1.1.x, because of the move from strings to foreign keys
class Command(BaseCommand):
    """
    A management command to migrate data for SimpleWiki from version 1.0.x to 1.1.x

    This command handles the migration of menu items and sections from the previous version.
    """

    def handle(self, *args, **kwargs):
        # ANSI escape codes for some colors
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'

        print("===== Menu =====")

        menu_item_parents = MenuItem.objects.filter(Q(parent='') | Q(parent=None))

        if import_parent_menus(menu_item_parents):
            print(GREEN + "Successfully migrated all parent menus from 1.0.x to 1.1.x" + RESET)
        else:
            print(RED + "Encountered errors while migrating all parent menus from 1.0.x to 1.1.x" + RESET)

        menu_item_children = MenuItem.objects.exclude(Q(parent='') | Q(parent=None))

        if import_child_menus(menu_item_children):
            print(GREEN + "Successfully migrated all child menus from 1.0.x to 1.1.x" + RESET)
        else:
            print(RED + "Encountered errors while migrating all child menus from 1.0.x to 1.1.x" + RESET)

        print("===== Section =====")

        section_items = SectionItem.objects.all()

        if import_sections(section_items):
            print(GREEN + "Successfully migrated all sections from 1.0.x to 1.1.x" + RESET)
        else:
            print(RED + "Encountered errors while migrating all sections from 1.0.x to 1.1.x" + RESET)

        print(GREEN + "Successfully migrated all data" + RESET)

def import_parent_menus(menu_item_parents):
    """
    Imports parent menus from version 1.0.x to version 1.1.x.

    Args:
        menu_item_parents (list): A list of menu item parents to be imported.

    Returns:
        None
    """
    # ANSI escape codes for some colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    for old_menu_parent in menu_item_parents:
        if Menu.objects.filter(path=old_menu_parent.path).exists():
            print("Menu " + old_menu_parent.title + " already exists, skipping..")
            continue

        new_menu = Menu()
        if old_menu_parent.index:
            new_menu.index = old_menu_parent.index
        else:
            new_menu.index = 0
        if old_menu_parent.title:
            new_menu.title = old_menu_parent.title
        else:
            print("Found a menu without a title, skipping it..")
            continue
        if old_menu_parent.icon:
            new_menu.icon = old_menu_parent.icon
        else:
            new_menu.icon = ""
        if old_menu_parent.path:
            new_menu.path = old_menu_parent.path
        else:
            print("Found a menu without a path, skipping it..")
            continue
        new_menu.parent = None
        if old_menu_parent.groups:
            if old_menu_parent.groups == "none":
                new_menu.groups = ""
            else:
                new_menu.groups = old_menu_parent.groups
        else:
            new_menu.groups = ""
        new_menu.states = ""

        try:
            new_menu.save()
            test_saved_menu = Menu.objects.filter(path=old_menu_parent.path)
            if test_saved_menu.exists():
                print("Successfully migrated parent menu " + test_saved_menu.first().title)
        except Exception as e:
            print(RED + "Error while migrating parent menu " + old_menu_parent.title + " from 1.0.x to 1.1.x: " + RESET + str(e))
            return False

    return True

def import_child_menus(menu_item_children):
    """
    Import child menus from version 1.0.x to version 1.1.x.

    Args:
        menu_item_children (list): List of child menu items to be imported.

    Returns:
        None
    """
    # ANSI escape codes for some colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    for old_menu_child in menu_item_children:
        if Menu.objects.filter(path=old_menu_child.path).exists():
            print("Child menu " + old_menu_child.title + " already exists, skipping..")
            continue

        new_menu_child = Menu()
        if old_menu_child.index:
            new_menu_child.index = old_menu_child.index
        else:
            new_menu_child.index = 0
        if old_menu_child.title:
            new_menu_child.title = old_menu_child.title
        else:
            print("Found a menu child without a title, skipping..")
            continue
        if old_menu_child.icon:
            new_menu_child.icon = old_menu_child.icon
        else:
            new_menu_child.icon = ""
        if old_menu_child.path:
            new_menu_child.path = old_menu_child.path
        else:
            print("Found a menu child without a path, skipping..")
            continue
        if old_menu_child.groups:
            new_menu_child.groups = old_menu_child.groups
        else:
            new_menu_child.groups = ""
        new_menu_child.states = ""

        parent_menu = Menu.objects.filter(path=old_menu_child.parent)
        if parent_menu.exists():
            new_menu_child.parent = parent_menu.first()
        else:
            print(YELLOW + "Unable to assign parent menu to child menu " + old_menu_child.title + ", ignoring it.." + RESET)
            new_menu_child.parent = None

        try:
            new_menu_child.save()
            test_saved_menu = Menu.objects.filter(path=old_menu_child.path)
            if test_saved_menu.exists():
                print("Successfully migrated child menu " + test_saved_menu.first().title)
        except Exception as e:
            print(RED + "Error while migrating child menu " + old_menu_child.title + " from 1.0.x to 1.1.x: " + RESET + str(e))
            return False

    return True

def import_sections(section_items):
    """
    Import sections from section_items and migrate them from version 1.0.x to 1.1.x.

    Args:
        section_items (list): A list of section items to import.

    Returns:
        None
    """
    # ANSI escape codes for some colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    for section_item in section_items:
        if Section.objects.filter(title=section_item.title).exists():
            print("Section " + section_item.title + " already exists, skipping..")
            continue

        new_section = Section()
        if section_item.title:
            new_section.title = section_item.title
        else:
            print(YELLOW + "Found a section without a title, skipping.." + RESET)
            continue
        if section_item.index:
            new_section.index = section_item.index
        else:
            new_section.index = 0
        if section_item.icon:
            new_section.icon = section_item.icon
        else:
            new_section.icon = ""
        if section_item.content:
            new_section.content = section_item.content 
        else:
            new_section.content = ""
        
        assigned_menu = Menu.objects.filter(path=section_item.menu_path)
        if assigned_menu.exists():
            new_section.menu = assigned_menu.first()
        else:
            new_section.menu = None

        try:
            new_section.save()
            test_saved_section = Section.objects.filter(title=section_item.title)
            if test_saved_section.exists():
                print("Successfully migrated section " + test_saved_section.first().title + " from 1.0.x to 1.1.x")
        except Exception as e:
            print(RED + "Error while migrating section " + RESET + section_item.title + RED + " from 1.0.x to 1.1.x: " + RESET + str(e))
            return False

    return True