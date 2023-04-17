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
        isEditor = True
    else:
        isEditor = False

    context = {'menu_items': menu_items, 
               'permission': isEditor, 
               'section_items': section_items,
               'user_groups': list(request.user.groups.values_list('name', flat=True))}

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

    # Order all menus by their index from low to high
    allMenuItems = MenuItem.objects.all().order_by('index')

    # isEditor is needed to show or hide the admin menu in the header panel
    if request.user.has_perm('simplewiki.editor'):
        isEditor = True
    else:
        isEditor = False

    # Order all sections by their index to display them from left to right from low to hight
    # Also only show sections that are related to the currently selected menu
    filtered_pages = SectionItem.objects.filter(menu_path=menu_name).order_by('index')

    context = {'menu_items': allMenuItems, 
               'filtered_pages': filtered_pages,
               'permission': isEditor,
               'user_groups': list(request.user.groups.values_list('name', flat=True))}
    
    # Check if the user has the permission to see the requested page. If not, send an error
    requestedMenu = MenuItem.objects.get(path=menu_name)
    if not requestedMenu.group or requestedMenu.group in list(request.user.groups.values_list('name', flat=True)):
        return render(request, 'simplewiki/dynamic_page.html', context)
    else:
        error_message = "You don\'t have the permissions to access this page. You need to be in the <b>" + requestedMenu.group + "</b> group on auth."
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
            searchResults = SectionItem.objects.filter(
                Q(content__icontains=query) | Q(title__icontains=query))
            context.update({'oldQuery': query})
            context.update({'searchResults': searchResults})
    except PermissionDenied as e:
        context.update({'error_msg': 'Unable to complete search: Do you have the right permissions to access this search?'})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        frame = inspect.currentframe()
        context.update({'error_django': str(e)})
        filename = inspect.getframeinfo(frame).filename
        linenumber = inspect.getframeinfo(frame).lineno
        context.update({'error_msg': 'Unknown error in ' + filename + ' in line ' + str(linenumber)})
        return render(request, 'simplewiki/error.html', context)

    return render(request, "simplewiki/search.html", context)

### Admin Views ###

@login_required
@permission_required("simplewiki.editor")
def admin_menus(request: WSGIRequest) -> HttpResponse:
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
            return handle_menu_create(request, context)
        elif edit:
            return handle_menu_edit(request, context, edit)
        elif delete:
            return handle_menu_delete(request, context, delete)

    # GET requests functions handle which button was pressed and which POST form to display
    elif request.method == 'GET':
        if create:
            context.update({'user_action': 'create'})
        elif edit:
            handle_menu_edit_get(request, context, edit)
        elif delete:
            handle_menu_delete_get(request, context, delete)
        else:
            # Just list all sections if no button was pressed
            context.update({'user_action': 'none'})

    return render(request, "simplewiki/admin/admin_menus.html", context)

def admin_sections(request: WSGIRequest) -> HttpResponse:
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
            return handle_section_create(request, context)
        elif edit:
            return handle_section_edit(request, context, edit)
        elif delete:
            return handle_section_delete(request, context, delete)
    
    # GET requests functions handle which button was pressed and which POST form to display
    if request.method == 'GET':
        if create:
            context.update({'user_action': 'create'})
        elif edit:
            # Is parsing the GET values and starts the first model queries for edit
            handle_section_edit_get(request, context, edit)
        elif delete:
            # Is parsing the GET values and starts the first model queries for delete
            handle_section_delete_get(request, context, delete)
        else:
            # Just list all sections if no button was pressed
            context.update({'user_action': 'none'})

    return render(request, "simplewiki/admin/admin_sections.html", context)

