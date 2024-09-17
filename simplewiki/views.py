"""App Views"""

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

@login_required
@permission_required("simplewiki.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view, will redirect the user to either an error message, saying no 
    menu items have been created or will redirect the user to the first menu 
    item they have access to (the one with the lowest index)
    
    Args:
        request (WSGIRequest): The standard django request

    Returns:
        HttpResponse: Returns the template and context to render
    """

    context = gen_context(request)

    # Only get parent menus
    menus = Menu.objects.filter(parent=None).order_by("index")

    user_groups = list(request.user.groups.values_list('name', flat=True))
    user_state = request.user.profile.state.name

    if menus.count() > 0:
        for parent_menu in menus:
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

            # Get all child menus associated with parent_menu
            child_menus = parent_menu.children.all().order_by("index")

            if child_menus.count() > 0:
                for child_menu in child_menus:
                    # Extract and format permission for child menu
                    child_group_names, child_state_names = None, None
                    if child_menu.groups is not None or child_menu.states is not None:
                        child_group_names = child_menu.groups.split(',')
                        child_state_names = child_menu.states.split(',')

                    # If child menu has groups AND user does not have permission to access the child menu
                    if (child_menu.groups and not any(child_group_name in user_groups for child_group_name in child_group_names)):
                        continue
                    # If child menu has states AND user does not have permission to access the child menu
                    elif child_menu.states and not any(user_state == state for state in child_state_names):
                        continue
                    else:
                        return redirect('simplewiki:dynamic_menu', child_menu.path)  

                # Navigate to the next menu parent if no children are accessable
                continue
            else:
                return redirect('simplewiki:dynamic_menu', parent_menu.path)
    
    error_message = "So far you didn't create any menus. Please create one under Editor -> Edit Menus"
    context.update({'error_code': "NO_MENU_AVAILABLE"})
    context.update({'error_alert': "info"})
    context.update({'error_msg': error_message})

    logger_msg = f'Unable to render any menus: No menus created.'
    logger.error(logger_msg)

    return render(request, "simplewiki/error.html", context)


@login_required
@permission_required("simplewiki.basic_access")
def dynamic_menus(request: WSGIRequest, menu_path: str) -> HttpResponse:
    """
    Dynamic Page View, renders a page based on the URL. This view will check 
    if the model has an object with the same url as the url, load it and 
    render it.

    Args:
        request (WSGIRequest): The standard django request
        menu_name (str): The url the user is requesting  

    Returns:
        HttpResponse: Returns the template and context to render
    """

    context = gen_context(request)

    menu = Menu.objects.get(path=menu_path)
    sections = Section.objects.filter(menu=menu).order_by('index')
    sections_count = sections.count()

    context.update({'available_sections': sections})
    context.update({'available_sections_count': sections_count})

    try: 
        latest_section = Section.objects.filter(menu=menu).latest('last_edit_date')
        context.update({'latest': True})
        context.update({'latest_section': latest_section})
    except Exception as e: 
        context.update({'latest': False})
        print("Unable to find latest section")

    # Split all group names. All group names need to be seperated by a comma
    try:
        group_names = menu.groups.split(',')
    except Exception as e:
        group_names = ""

    context.update({'group_names': group_names})

    if any(group_name in request.user.groups.values_list('name', flat=True) for group_name in group_names) or any(element == "none" or not element for element in group_names):
        
        if not menu.states or request.user.profile.state.name in menu.states:

            # If menu is a menu with submenus, then throw an error
            if menu.children.count() > 0:
                context.update({'error_code': 'USER_MENU_SUBMENU_ERROR'})
                error_message = "This menu has at least one submenu, please navigate to that one instead."
                context.update({'error_msg': error_message})
        
                return render(request, 'simplewiki/error.html', context)
            # If menu is a menu without submenus, render the page
            else:
                logger_msg = f'Rendering wiki page "{menu_path}" for user "{request.user}".'
                logger.info(logger_msg)

                return render(request, 'simplewiki/dynamic_page.html', context)
        # Missing state permission
        else:
            context.update({'error_code': 'USER_PERMISSION_MISSING_STATE'})
            error_message = "You don\'t have the permissions to access this page. You need to be in the <b>" + menu.states + "</b> state."
            context.update({'error_msg': error_message})
        
            return render(request, 'simplewiki/error.html', context)
    # Missing group permission
    else:
        requested_groups = menu.groups.replace(',', ', ')
        logger_msg = f'Rejected rendering request for menu "{menu_path}", user "{request.user}" doesn\'t have neccessary groups "{requested_groups}"'
        logger.info(logger_msg)

        # If more then two groups are required
        if len(menu.groups.split(',')) > 1:
            group_plural = "groups"
        else:
            group_plural = "group"
        context.update({'error_code': 'USER_PERMISSION_MISSING_GROUP'})
        error_message = "You don\'t have the permissions to access this page. You need to be in the <b>" + menu.groups.replace(',', ', ') + "</b> " + group_plural + " on auth."
        context.update({'error_msg': error_message})
        
        return render(request, 'simplewiki/error.html', context)

    return render(request, 'simplewiki/dynamic_page.html', context)

@login_required
@permission_required("simplewiki.basic_access") 
def search(request: WSGIRequest) -> HttpResponse:
    """
    Search View, renders the search function and handles the search itself. 
    Once the user types anything into the search bar and hits enter, this
    view will search all section's title and context about the search, while 
    ignoring case-sensitivity 

    Args:
        request (WSGIRequest): The standard django request

    Returns:
        HttpResponse: Returns the template and context to render
    """

    context = gen_context(request)

    try:
        query = request.GET.get('query')

        available_results = []
        if query:
            # Search all sections' contexts and titles
            search_results = Section.objects.filter(
                Q(content__icontains=query) | Q(title__icontains=query))
            
            # Get the menu for every search results
            for result in search_results:
                #result_menu = Menu.objects.get(path=result.menu_path)
                result_menu = result.menu

                group_names = result_menu.groups.split(',')
                user_groups = list(request.user.groups.values_list('name', flat=True))

                # TODO: Really bad, sometimes groups is "none" and sometimes "None", fix asap
                # Check if the user can access the corresponding menu
                if result_menu.groups == "" or len(result_menu.groups) == 0 or any(group_name in user_groups for group_name in group_names):
                    if result_menu.states == "" or len(result_menu.states) == 0 or request.user.profile.state.name in result_menu.states.split(','):
                        available_results.append(result)
            
            context.update({'available_results': available_results})
            context.update({'oldQuery': query})
    except PermissionDenied as e:
        context.update({'error_code': 'USER_SEARCH_NO_PERMISSIONS'})
        context.update({'error_msg': 'Unable to complete search: Do you have the right permissions to access this search?'})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        frame = inspect.currentframe()
        context.update({'error_code': 'USER_SEARCH_UNKNOWN'})
        context.update({'error_django': str(e)})
        file_name = inspect.getframeinfo(frame).filename
        line_number = inspect.getframeinfo(frame).lineno
        context.update({'error_msg': 'Unknown error in ' + file_name + ' in line ' + str(line_number)})

        return render(request, 'simplewiki/error.html', context)

    return render(request, "simplewiki/search.html", context)

### Editor

@login_required
@permission_required("simplewiki.editor_access")
def editor_menus(request: WSGIRequest) -> HttpResponse:
    """
    This function is a Django view that handles all list, create, edit and delete operations related to menus.
    It uses GET requests to check what button was pressed and then uses POST requests to store and save the data inside the model.

    Args:
        request (WSGIRequest): The standard Django request.

    Returns:
        HttpResponse: Returns the template and context to render.
    """

    context = gen_context(request)

    create = request.GET.get('create')
    edit = request.GET.get('edit')
    delete = request.GET.get('delete')

    # POST requests functions handle the actual create, edit and delete operations
    if request.method == 'POST':
        if create:
            return create_new_menu(request, context)
        elif edit:
            return edit_existing_menu(request, context, edit)
        elif delete:
            return delete_existing_menu(request, context, delete)

    # GET requests functions handle which button was pressed and which POST form to display
    elif request.method == 'GET':
        if create:
            context.update({'user_action': 'create'})
        elif edit:
            load_menu_edit_form(request, context, edit)
        elif delete:
            load_menu_delete_form(request, context, delete)
        else:
            # Just list all sections if no button was pressed
            context.update({'user_action': 'none'})

    return render(request, "simplewiki/editor/editor_menus.html", context)


@login_required
@permission_required("simplewiki.editor_access")
def editor_sections(request: WSGIRequest) -> HttpResponse:
    """
    This function is a Django view that handles all list, create, edit and delete operations related to sections.
    It requires the user to be logged in and have the "simplewiki.editor_access" permission.
    It uses GET requests to check what button was pressed and then uses POST requests to store and save the data inside the model.

    Args:
        request (WSGIRequest): The standard Django request object.

    Returns:
        HttpResponse: Returns the template and context to render.
    """

    context = gen_context(request)

    create = request.GET.get('create')
    edit = request.GET.get('edit')
    delete = request.GET.get('delete')

    # POST requests functions handle the actual create, edit and delete operations
    if request.method == 'POST':
        if create:
            return create_new_section(request, context)
        elif edit:
            return edit_existing_section(request, context, edit)
        elif delete:
            return delete_existing_section(request, context, delete)
    
    # GET requests functions handle which button was pressed and which POST form to display
    if request.method == 'GET':
        if create:
            context.update({'user_action': 'create'})
        elif edit:
            # Is parsing the GET values and starts the first model queries for edit
            load_section_edit_form(request, context, edit)
        elif delete:
            # Is parsing the GET values and starts the first model queries for delete
            load_section_delete_form(request, context, delete)
        else:
            # Just list all sections if no button was pressed
            context.update({'user_action': 'none'})

    return render(request, "simplewiki/editor/editor_sections.html", context)

@login_required
@permission_required("simplewiki.editor_access")
def editor_sort(request: WSGIRequest) -> HttpResponse:
    """
    Renders the sortable menu editor view.

    Args:
        request (WSGIRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.
    """

    context = gen_context(request)

    return render(request, "simplewiki/editor/editor_sort.html", context)

### JSON post 

@login_required
@permission_required("simplewiki.editor_access")
def editor_sort_post(request: WSGIRequest):
    """
    This function handles the sorting of menus in the editor view.
    It receives a POST request with a JSON object containing the new order of the menus.
    The function then updates the index and parent fields of each menu object in the database
    based on the information provided in the JSON object.
    If any error occurs during the process, the function returns a JSON response with an error message.
    """

    try:
        data = json.loads(request.POST.get('data'))

        number = 0

        # Trying to store data and sort menus based on data (json)
        for item in data:
            try:
                parent_title = item["id"]
                parent = Menu.objects.get(title=parent_title)
                parent.index = number
                parent.parent = None
                parent.save()
                
                number = number + 1
            except Exception as e:
                return JsonResponse({"status": "error", "message": "Unable to save parent '" + parent_title + "':" + str(e)})
            children = item.get("children", [])
            for child in children:
                try:
                    child_title = child["id"]
                    child = Menu.objects.get(title=child_title)
                    child.index = number
                    child.parent = Menu.objects.get(title=parent_title)
                    child.save()
                    number = number + 1
                except Exception as e:
                    return JsonResponse({"status": "error", "message": "Unable to save child '" + child_title + "':" + str(e)})

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


