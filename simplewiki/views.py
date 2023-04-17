"""App Views"""

# Python imports
import inspect

# Django imports
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.exceptions import PermissionDenied

# Custom imports
from .models import MenuItem, SectionItem
from .admin_helper import *

### Helper Functions ###

# Standard context for a normal view, required by base.html
def genContext(request: WSGIRequest):
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

    if request.user.has_perm('simplewiki.editor'):
        is_editor = True
    else:
        is_editor = False

    current_path = request.path

    context = {'menu_items': menu_items, 
               'is_editor': is_editor, 
               'section_items': section_items,
               'user_groups': list(request.user.groups.values_list('name', flat=True)),
               'current_path': current_path}

    return context

### User Views ###

@login_required
@permission_required("simplewiki.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view, will redirect the user to either an error message, saying no 
    menu items have been created or will redirect the user to the first menu 
    item (the one with the lowest index)
    
    Args:
        request (WSGIRequest): The standard django request

    Returns:
        HttpResponse: Returns the template and context to render
    """

    context = genContext(request)

    menu_items = MenuItem.objects.all()

    # Show the first wiki page 
    if menu_items.count() > 0:
        return redirect('simplewiki:dynamic_menu', menu_items.order_by('index').first())
    # Show a default "create your first page.." error page
    else:
        error_message = "So far you didn't create any menus. Please create one under Admin -> Menus"
        context.update({'error_msg': error_message})
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

    context = genContext(request)
    context.update({'available_sections': available_sections})
    
    # Check if the user has the permission to see the requested page. If not, send an error
    requested_menu = MenuItem.objects.get(path=menu_name)

    # Split all group names. All group names need to be seperated by a comma
    try:
        group_names = requested_menu.groups.split(',')
    except Exception as e:
        group_names = ""
    
    context.update({'group_names': group_names})
    print("Test")

    #if not requested_menu.groups or requested_menu.groups in list(request.user.groups.values_list('name', flat=True)):
    if not requested_menu.groups or any(group_name in request.user.groups.values_list('name', flat=True) for group_name in group_names):
        return render(request, 'simplewiki/dynamic_page.html', context)
    else:
        error_message = "You don\'t have the permissions to access this page. You need to be in the <b>" + requested_menu.groups.replace(',', ', ') + "</b> groups on auth."
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

    context = genContext(request)

    try:
        query = request.GET.get('query')
        if query:
            search_results = SectionItem.objects.filter(
                Q(content__icontains=query) | Q(title__icontains=query))
            context.update({'oldQuery': query})
            context.update({'searchResults': search_results})
    except PermissionDenied as e:
        context.update({'error_msg': 'Unable to complete search: Do you have the right permissions to access this search?'})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        frame = inspect.currentframe()
        context.update({'error_django': str(e)})
        file_name = inspect.getframeinfo(frame).filename
        line_number = inspect.getframeinfo(frame).lineno
        context.update({'error_msg': 'Unknown error in ' + file_name + ' in line ' + str(line_number)})
        return render(request, 'simplewiki/error.html', context)

    return render(request, "simplewiki/search.html", context)

### Admin Views ###

@login_required
@permission_required("simplewiki.editor")
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

    context = genContext(request)

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

    context = genContext(request)

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

