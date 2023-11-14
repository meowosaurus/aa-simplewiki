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

# Custom imports
from .models import MenuItem, SectionItem
from .admin_helper_menus import *
from .admin_helper_sections import *

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

    menu_items = MenuItem.objects.all().order_by('index')
    section_items = SectionItem.objects.all().order_by('index')

    if request.user.has_perm('simplewiki.editor_access'):
        is_editor = True
    else:
        is_editor = False

    current_path = request.path

    all_groups = Group.objects.all()
    user_state = request.user.profile.state.name

    context = {'menu_items': menu_items, 
               'is_editor': is_editor, 
               'section_items': section_items,
               'user_groups': list(request.user.groups.values_list('name', flat=True)),
               'user_state': user_state,
               'current_path': current_path,
               'all_groups': all_groups}

    return context

### User Views ###

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

    menu_items = MenuItem.objects.all()

    # If the menu even has menu items
    if menu_items.count() > 0:
        # Get all parent menus
        for parent_menu_item in MenuItem.objects.filter(parent="").order_by("index"):

            # Get all sub menus for the current parent menu
            first_menu_submenus = MenuItem.objects.filter(parent=parent_menu_item.path).order_by("index")

            # If the menu even has submenus
            if first_menu_submenus.count() > 0:
                for first_menu_item in first_menu_submenus:
                    # If the submenu has any groups
                    if first_menu_item.groups:
                        group_names = first_menu_item.groups.split(',')
                        user_groups = list(request.user.groups.values_list('name', flat=True))

                        logger_msg = f'Menu "{parent_menu_item.title}" has submenu "{first_menu_item.title}", checking if user "{request.user}" has permission to access it.'
                        logger.info(logger_msg)

                        # If the user has the right to access this submenu
                        if any(group_name in user_groups for group_name in group_names) or any(element == "none" for element in group_names):
                            return redirect('simplewiki:dynamic_menu', first_menu_item)
                    else:
                        return redirect('simplewiki:dynamic_menu', first_menu_item)
            # If the menu doesn't have submenus
            else:
                logger_msg = f'Unable to find any submenus for "{parent_menu_item}", checking if user "{request.user}" has permission to access it.'
                logger.info(logger_msg)

                # If the parent menu has any groups
                if parent_menu_item.groups:
                    group_names = parent_menu_item.groups.split(',')
                    user_groups = list(request.user.groups.values_list('name', flat=True))

                    # If the user has the right to access the parent menu
                    if any(group_name in user_groups for group_name in group_names) or any(element == "none" for element in group_names):
                        return redirect('simplewiki:dynamic_menu', parent_menu_item)
                else:
                    

                    return redirect('simplewiki:dynamic_menu', parent_menu_item)

        # If there are no menus the user has permission to access
        error_code = "#1000"
        error_message = "You don't have the permission to access any menus. Please contact the administrator."
        context.update({'error_code': error_code})
        context.update({'error_msg': error_message})

        logger_msg = f'Unable to render any menus: User "{request.user}" doesn\'t have the permission to access any menus.'
        logger.error(logger_msg)

        return render(request, "simplewiki/error.html", context)
    # Show a default "create your first menu.." error page
    else:
        error_code = "#1000"
        error_message = "So far you didn't create any menus. Please create one under Admin -> Menus"
        context.update({'error_code': error_code})
        context.update({'error_msg': error_message})

        logger_msg = f'Unable to render any menus: No menus created.'
        logger.error(logger_msg)

        return render(request, "simplewiki/error.html", context)

@login_required
@permission_required("simplewiki.basic_access")
def dynamic_menus(request: WSGIRequest, menu_name: str) -> HttpResponse:
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

    # Order all sections by their index to display them from left to right from low to hight
    # Also only show sections that are related to the currently selected menu
    available_sections = SectionItem.objects.filter(menu_path=menu_name).order_by('index')

    context = gen_context(request)
    context.update({'available_sections': available_sections})
    
    # Check if the user has the permission to see the requested page. If not, send an error
    requested_menu = MenuItem.objects.get(path=menu_name)

    # Split all group names. All group names need to be seperated by a comma
    try:
        group_names = requested_menu.groups.split(',')
    except Exception as e:
        group_names = ""

    context.update({'group_names': group_names})

    print(not requested_menu.states)

    #if not requested_menu.groups or requested_menu.groups in list(request.user.groups.values_list('name', flat=True)):
    if any(group_name in request.user.groups.values_list('name', flat=True) for group_name in group_names) or any(element == "none" or not element for element in group_names):
        
        if not requested_menu.states or request.user.profile.state.name in requested_menu.states:

            logger_msg = f'Rendering wiki page "{menu_name}" for user "{request.user}".'
            logger.info(logger_msg)

            return render(request, 'simplewiki/dynamic_page.html', context)
        else:
            context.update({'error_code': 'SIMPLEWIKI_PERMISSION_MISSING_STATE'})
            error_message = "You don\'t have the permissions to access this page. You need to be in the <b>" + requested_menu.states + "</b> state."
            context.update({'error_msg': error_message})
        
            return render(request, 'simplewiki/error.html', context)
    else:
        requested_groups = requested_menu.groups.replace(',', ', ')
        logger_msg = f'Rejected rendering request for menu "{menu_name}", user "{request.user}" doesn\'t have neccessary groups "{requested_groups}"'
        logger.info(logger_msg)

        # If more then two groups are required
        if len(requested_menu.groups.split(',')) > 1:
            group_plural = "groups"
        else:
            group_plural = "group"
        context.update({'error_code': 'SIMPLEWIKI_PERMISSION_MISSING_GROUP'})
        error_message = "You don\'t have the permissions to access this page. You need to be in the <b>" + requested_menu.groups.replace(',', ', ') + "</b> " + group_plural + " on auth."
        context.update({'error_msg': error_message})
        
        return render(request, 'simplewiki/error.html', context)

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
            search_results = SectionItem.objects.filter(
                Q(content__icontains=query) | Q(title__icontains=query))
            
            # Get the menu for every search results
            for result in search_results:
                print(result)
                result_menu = MenuItem.objects.get(path=result.menu_path)

                group_names = result_menu.groups.split(',')
                user_groups = list(request.user.groups.values_list('name', flat=True))

                # TODO: Really bad, sometimes groups is "none" and sometimes "None", fix asap
                # Check if the user can access the corresponding menu
                if result_menu.groups == "none" or result_menu.groups == "None" or len(result_menu.groups) == 0 or any(group_name in user_groups for group_name in group_names):
                    available_results.append(result)
            
            context.update({'available_results': available_results})
            context.update({'oldQuery': query})
    except PermissionDenied as e:
        context.update({'error_code': 'SIMPLEWIKI_SEARCH_NO_PERMISSIONS'})
        context.update({'error_msg': 'Unable to complete search: Do you have the right permissions to access this search?'})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        frame = inspect.currentframe()
        context.update({'error_code': 'SIMPLEWIKI_SEARCH_UNKNOWN'})
        context.update({'error_django': str(e)})
        file_name = inspect.getframeinfo(frame).filename
        line_number = inspect.getframeinfo(frame).lineno
        context.update({'error_msg': 'Unknown error in ' + file_name + ' in line ' + str(line_number)})

        return render(request, 'simplewiki/error.html', context)

    return render(request, "simplewiki/search.html", context)

### Admin Views ###

@login_required
@permission_required("simplewiki.editor_access")
def editor_menus(request: WSGIRequest) -> HttpResponse:
    """
    Admin Menu View, this view is responsible for handling all list, create, edit
    and delete operations related to menus. It uses GET requests to check what button 
    was pressed and then uses POST requests to store and save the data inside the model

    Args:
        request (WSGIRequest): The standard django request

    Returns:
        HttpResponse: Returns the template and context to render
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
    Admin Sections View, this view is responsible for handling all list, create, edit
    and delete operations related to sections. It uses GET requests to check what button 
    was pressed and then uses POST requests to store and save the data inside the model

    Args:
        request (WSGIRequest): The standard django request

    Returns:
        HttpResponse: Returns the template and context to render
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
    context = gen_context(request)

    return render(request, "simplewiki/editor/editor_sort.html", context)

# JSON post 
@login_required
@permission_required("simplewiki.editor_access")
def editor_sort_post(request: WSGIRequest):
    try:
        data = json.loads(request.POST.get('data'))

        number = 0

        # Trying to store data and sort menus based on data (json)
        for item in data:
            try:
                parent_title = item["id"]
                parent = MenuItem.objects.get(title=parent_title)
                parent.index = number
                parent.parent = ""
                parent.save()
                
                number = number + 1
            except Exception as e:
                return JsonResponse({"status": "error", "message": "Unable to save parent '" + parent_title + "':" + str(e)})
            children = item.get("children", [])
            for child in children:
                try:
                    child_title = child["id"]
                    child = MenuItem.objects.get(title=child_title)
                    child.index = number
                    child.parent = parent.path
                    child.save()
                    number = number + 1
                except Exception as e:
                    return JsonResponse({"status": "error", "message": "Unable to save child '" + child_title + "':" + str(e)})

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

### Guides

@login_required
@permission_required("simplewiki.editor_access")
def editor_markdown_guide(request: WSGIRequest) -> HttpResponse:
    context = gen_context(request)

    return render(request, "simplewiki/guides/markdown.html", context)
