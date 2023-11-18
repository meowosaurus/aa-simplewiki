from django import template

from simplewiki.models import *

register = template.Library()

def is_user_in_groups(user_groups, group_list) -> bool:
    """
    is_user_in_groups is a template filter and checks if the 
    user has any of the required groups

    Params:
        user_groups (str): All groups held by the user
        group_list (str): All groups required by the menu

    Returns:
        bool: Returns true if the user is at least in one of the required groups
    """

    print(user_groups)
    print(group_list)

    #print(user_groups.split(','))

    #print(user_groups.split(','))
    print(group_list)
    print(user_groups in group_list)
    #print(user_groups.split(',') in group_list)
    #print(any(group in user_groups.split(',') for group in group_names))

    if user_groups in group_list:
        return True
    return False

    #groupa_list = None
    #group_names = group_list.split(',')
    #print("Group names: " + group_names)

    # Try to split group lists into any array based on comma
    #try:
    #    if group_list is not None:
    #        print("test2")
    #        print(type(group_list))
    #    if isinstance(group_list, str):
    #        print("test3")
    #        group_names = group_list.split(',')
    #    else:
    #        return False
    #except Exception as e:
    #    return False

    # Check if the user has any groups or if the menu doesn't even require any groups
    #print("Test")
    #print(str(any(group_name in user_groups for group_name in group_names)))
    #return any(group_name in user_groups for group_name in group_names)

def access_test(parent, user_groups):
    children = parent.children.all().order_by('index')

    for child in children:
        # If at least one submenu is accessable
        if is_user_in_groups(user_groups, child.groups):
            return True
        else:
            return False

def add_group_space(text: str) -> str:
    return text.replace(',', ', ')

def has_menu_children(menu_item):
    # If any other menu has menu_item as parent
    return MenuItem.objects.filter(parent=menu_item.path).exists()

def get_menu_children(menu_item):
    return Menu.objects.filter(parent=menu_item.path).order_by('index')

def get_submenu_paths(parent_menu_path):
    """
    Returns a list of paths for the submenus of a given parent menu item.

    Args:
        parent_menu_item (Menu): The parent menu item.

    Returns:
        list: A list of paths for the submenus of the parent menu item.
    """
    paths = []

    children = Menu.objects.get(path=parent_menu_path).children.order_by('index')
    for child in children:
        paths.append("/wiki/" + child.path + "/")

    return paths

def children_order_by(menu):
    return Menu.objects.filter(parent=menu).order_by("index")

def menu_childmenus_accessable(menu, user_groups, user_state):

    if not menu.groups or menu.groups in user_groups:
        if not menu.states or menu.states in user_state:
            children = menu.children.all()

            if user_access_any_submenus(menu, user_groups, user_state):
                return True

    return False

@register.simple_tag
def any_paths_current(current_path, children_paths):
    return current_path in children_paths

@register.simple_tag
def user_access_any_submenus(parent_menu, user_groups, user_state):
    """
    This function checks if the user has access to any submenus of a given parent menu.
    It takes in the parent_menu object and the request object as parameters.
    It returns True if the user has access to any submenus, False otherwise.
    """
    submenus = parent_menu.children.all()

    #for submenu in submenus:
    #    return
        #if not submenu.groups or is_user_in_groups(user_groups, submenu.groups):
        #    if not submenu.states or is_user_in_groups(user_state, submenu.states):
        #        #print("User is accessing " + parent_menu.title + " has access to submenu: " + submenu.title)
        #        return True
    return False

register.filter('is_user_in_groups', is_user_in_groups)
register.filter('add_group_space', add_group_space)
register.filter('has_menu_children', has_menu_children)
register.filter('get_menu_children', get_menu_children)
register.filter('children_order_by', children_order_by)
register.filter('get_submenu_paths', get_submenu_paths)
register.filter('any_paths_current', any_paths_current)
register.filter('user_access_any_submenus', user_access_any_submenus)
register.filter('menu_childmenus_accessable', menu_childmenus_accessable)
register.filter('access_test', access_test)