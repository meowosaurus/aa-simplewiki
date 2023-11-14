from django import template

from simplewiki.models import *

register = template.Library()

def is_user_in_groups(user_groups, group_list) -> bool:
    """
    is_user_in_groups is a template filter and checks if the 
    user has any of the required groups

    Params:
        user_groups: All groups held by the user
        group_list: All groups required by the menu

    Returns:
        bool: Returns true if the user is at least in one of the required groups
    """

    # Try to split group lists into any array based on comma
    try:
        if group_list is not None and isinstance(group_list, str):
            group_names = group_list.split(',')
        else:
            return False
    except Exception as e:
        return False

    # Check if the user has any groups or if the menu doesn't even require any groups
    return any(group_name in user_groups for group_name in group_names) or any(group_name == "none" for group_name in group_names)

def add_group_space(text: str) -> str:
    return text.replace(',', ', ')

def has_menu_children(menu_item):
    # If any other menu has menu_item as parent
    return MenuItem.objects.filter(parent=menu_item.path).exists()

def get_menu_children(menu_item):
    return Menu.objects.filter(parent=menu_item.path).order_by('index')

def get_submenu_paths(parent_menu_item):
    paths = []

    children = Menu.objects.filter(parent=parent_menu_item).order_by('index')
    for child in children:
        paths.append("/wiki/" + child.path + "/")

    return paths

def children_order_by(menu):
    return Menu.objects.filter(parent=menu).order_by("index")

@register.simple_tag
def any_paths_current(current_path, children_paths):
    return current_path in children_paths

@register.simple_tag
def user_access_any_submenus(parent_menu, user_groups):
    submenus = MenuItem.objects.filter(parent=parent_menu.path)

    for submenu in submenus:
        if not submenu.groups or is_user_in_groups(user_groups, submenu.groups):
            return True
    return False

register.filter('is_user_in_groups', is_user_in_groups)
register.filter('add_group_space', add_group_space)
register.filter('has_menu_children', has_menu_children)
register.filter('get_menu_children', get_menu_children)
register.filter('children_order_by', children_order_by)
register.filter('get_submenu_paths', get_submenu_paths)
register.filter('any_paths_current', any_paths_current)
register.filter('user_access_any_submenus', user_access_any_submenus)