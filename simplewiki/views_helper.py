# Python imports
import inspect
import json 

# Django imports
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from allianceauth.services.hooks import get_extension_logger
from allianceauth.authentication.models import State

# Custom imports
from .models import *
from .admin_helper_menus import *
from .admin_helper_sections import *
from .app_settings import simplewiki_display_page_contents
from .views_helper import *

from app_utils.logging import LoggerAddTag
from . import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

### Helper Functions ###

# Standard context for a normal view, required by base.html
def gen_context(request: WSGIRequest):
    """
    Generates the standard context for the django render function, 
    context includes all menu and section items, if the user is 
    an editor and all user groups (managed by aa)

    Args:
        request (WSGIRequest): The standard django request

    Returns:
        dict: Returns the standard context used for all views 
    """

    menu_items = Menu.objects.all().order_by('index')
    section_items = Section.objects.all().order_by('index')

    if request.user.has_perm('simplewiki.editor_access'):
        is_editor = True
    else:
        is_editor = False

    current_path = request.path

    all_groups = Group.objects.all()
    all_states = State.objects.all()
    user_groups = list(request.user.groups.values_list('name', flat=True))
    user_state = request.user.profile.state.name

    context = {'menu_items': menu_items, 
               'is_editor': is_editor, 
               'section_items': section_items,
               'user_groups': user_groups,
               'user_state': user_state,
               'current_path': current_path,
               'all_groups': all_groups,
               'all_states': all_states,
               'request': request,
               # OPTIONS
               'display_page_contents': simplewiki_display_page_contents}

    generate_menu(context, user_groups, user_state)

    return context

def children_accessable(request, children):
    user_groups = list(request.user.groups.values_list('name', flat=True))

    for child in children:
        if not child.groups or child.groups in user_groups:
            if not child.states or child.states == request.user.profile.state.name:
                return True

    return False

def generate_menu(context, user_groups, user_state):
    navbar = []

    parent_menus = Menu.objects.filter(parent=None).order_by('index')

    for parent_menu in parent_menus:

        # Extract and format permissions for parent menu
        group_names, state_names = "", ""
        if parent_menu.groups or parent_menu.states:
            group_names = parent_menu.groups.split(',')
            state_names = parent_menu.states.split(',')

        # If parent menu has groups AND user does not have permission to access the parent menu
        if parent_menu.groups and not any(group_name in user_groups for group_name in group_names):
            continue

        # If parent menu has states AND user does not have permission to access the parent menu
        if parent_menu.states and not any(user_state == state for state in state_names):
            continue

        parent_item = {'title': parent_menu.title, 'path': parent_menu.path, 'icon': parent_menu.icon}

        child_menus = parent_menu.children.all().order_by('index')

        parent_item['submenus'] = []

        if child_menus.count() > 0:

            for child_menu in child_menus:
                # Extract and format permission for child menu
                child_group_names, child_state_names = None, None
                if child_menu.groups is not None or child_menu.states is not None:
                    child_group_names = child_menu.groups.split(',')
                    child_state_names = child_menu.groups.split(',')

                # If child menu has groups AND user does not have permission to access the child menu
                if (child_menu.groups and not any(child_group_name in user_groups for child_group_name in child_group_names)):
                    continue
                
                # If child menu has states AND user does not have permission to access the child menu
                if child_menu.states and not user_state in child_menu.states.split(','):
                    continue

                sub_item = {'title': child_menu.title, 'path': child_menu.path, 'icon': child_menu.icon}
                parent_item['submenus'].append(sub_item)

        if len(parent_item['submenus']) == 0 and child_menus.count() > 0:
            continue
        
        navbar.append(parent_item)

    context.update({'navbar': navbar})
