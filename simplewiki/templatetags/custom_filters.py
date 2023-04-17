from django import template

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

    splitted_list = group_list.split(',')

    if not group_list:
        return False
    return any(group_name in user_groups for group_name in splitted_list)

register = template.Library()

register.filter('is_user_in_groups', is_user_in_groups)