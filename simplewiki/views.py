"""App Views"""

import inspect

# Django imports
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.db import IntegrityError
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models.deletion import ProtectedError

# Custom imports
from .models import MenuItem, SectionItem

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

def handle_menu_create(request: WSGIRequest, context: dict) -> HttpResponse:
    """
    Handle Menu Create will check the data, sent by the user via the form via a POST
    request and then store it. This function creates a new model object and stores it.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template

    Returns:
        HttpResponse: Returns the template and context to render
    """

    if request.POST['confirm_create'] == '1':
        newMenu = MenuItem()

        # Fill newMenu with variables and check for errors
        keys = ['index', 'title', 'icon', 'group']
        for key in keys:
            try:
                if key == 'index':
                    setattr(newMenu, key, int(request.POST[key]))
                else:
                    setattr(newMenu, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            except Exception as e:
                frame = inspect.currentframe()
                context.update({'error_django': str(e)})
                filename = inspect.getframeinfo(frame).filename
                linenumber = inspect.getframeinfo(frame).lineno
                context.update({'error_msg': 'Unknown error in ' + filename + ' in line ' + str(linenumber)})
                return render(request, 'simplewiki/error.html', context)
                    
        # Taking the titel and converting it into a url suitable string
        newMenu.path = slugify(request.POST['title'])
                
        # Save newMenu and check for errors
        try:
            newMenu.save()
        except (IntegrityError, ValidationError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            frame = inspect.currentframe()
            context.update({'error_django': str(e)})
            filename = inspect.getframeinfo(frame).filename
            linenumber = inspect.getframeinfo(frame).lineno
            context.update({'error_msg': 'Unknown error in ' + filename + ' in line ' + str(linenumber)})
            return render(request, 'simplewiki/error.html', context)

        print("Yeeeeeeeeeeeeeeeeep")
        return redirect("simplewiki:admin_menus")
    else:
        return redirect("simplewiki:admin_menus")

def handle_menu_edit(request: WSGIRequest, context: dict, edit: str) -> HttpResponse:
    """
    Handle Menu Edit will check the data, sent by the user via the form via a POST
    request and then store it. This function requests an existing model object and 
    overwrites it.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template
        edit (str): The GET request's value for "edit"

    Returns:
        HttpResponse: Returns the template and context to render
    """

    # If do edit operation
    if request.POST['confirm_edit'] == '1':
        try:
            selectedMenu = MenuItem.objects.get(path=edit)
        except MenuItem.DoesNotExist as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            frame = inspect.currentframe()
            context.update({'error_django': str(e)})
            filename = inspect.getframeinfo(frame).filename
            linenumber = inspect.getframeinfo(frame).lineno
            context.update({'error_msg': 'Unknown error in ' + filename + ' in line ' + str(linenumber)})
            return render(request, 'simplewiki/error.html', context)

        # Fill selectedMenu with new variables and check for errors
        keys = ['index', 'title', 'icon', 'group']
        for key in keys:
            try: 
                # Check if user changed a value. If they did, save the new one.
                if request.POST[key]:
                    if key == 'index':
                        setattr(selectedMenu, key, int(request.POST[key]))
                    else:
                        setattr(selectedMenu, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            except Exception as e:
                frame = inspect.currentframe()
                context.update({'error_django': str(e)})
                filename = inspect.getframeinfo(frame).filename
                linenumber = inspect.getframeinfo(frame).lineno
                context.update({'error_msg': 'Unknown error in ' + filename + ' in line ' + str(linenumber)})
                return render(request, 'simplewiki/error.html', context)
                
        # Taking the titel and converting it into a url suitable string
        selectedMenu.path = slugify(request.POST['title'])

        # Save selectedMenu and check for errors
        try:
            selectedMenu.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            frame = inspect.currentframe()
            context.update({'error_django': str(e)})
            filename = inspect.getframeinfo(frame).filename
            linenumber = inspect.getframeinfo(frame).lineno
            context.update({'error_msg': 'Unknown error in ' + filename + ' in line ' + str(linenumber)})
            return render(request, 'simplewiki/error.html', context)
                
        return redirect("simplewiki:admin_menus")
    # If cancel edit operation
    elif request.POST['confirm_edit'] == '0':
        return redirect("simplewiki:admin_menus")
        
def handle_menu_delete(request: WSGIRequest, context: dict, delete: str) -> HttpResponse:
    """
    Handle Menu Delete will check the data, sent by the user via the form via a POST
    request and then store it. This function requests an existing model object and 
    deletes it.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template
        delete (str): The GET request's value for "delete"

    Returns:
        HttpResponse: Returns the template and context to render
    """

    # If do delete operation
    if request.POST['confirm_delete'] == '1':
        try:
            selectedMenu = MenuItem.objects.get(path=delete)
            selectedMenu.delete()
        except (MenuItem.DoesNotExist, ProtectedError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
                
        return redirect("simplewiki:admin_menus")
    # If cancel delete operation
    elif request.POST['confirm_delete'] == '0':
        return redirect("simplewiki:admin_menus")



def handle_menu_edit_get(request: WSGIRequest, context: dict, edit: str) -> HttpResponse:
    """
    Handle Menu Edit Get is the GET request helper function for editing menus. This function does 
    not read the GET value data, but only processes it. It takes the data and sends it via the context 
    to the template.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template
        delete (str): The GET request's value for "edit"

    Returns:
        HttpResponse: Returns the template and context to render
    """

    try:
        selectedMenu = MenuItem.objects.get(path=edit)
        context.update({'selectedMenu': selectedMenu})
        context.update({'user_action': 'edit'})
    except MenuItem.DoesNotExist as e:
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        frame = inspect.currentframe()
        context.update({'error_django': str(e)})
        filename = inspect.getframeinfo(frame).filename
        linenumber = inspect.getframeinfo(frame).lineno
        context.update({'error_msg': 'Unknown error in ' + filename + ' in line ' + str(linenumber)})
        return render(request, 'simplewiki/error.html', context)
    
def handle_menu_delete_get(request: WSGIRequest, context: dict, delete: str) -> HttpResponse:
    """
    Handle Menu Delete Get is the GET request helper function for deleting menus. This function does 
    not read the GET value data, but only processes it. It takes the data and sends it via the context 
    to the template.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template
        delete (str): The GET request's value for "edit"

    Returns:
        HttpResponse: Returns the template and context to render
    """

    try:
        selectedMenu = MenuItem.objects.get(path=delete)
        context.update({'selectedMenu': selectedMenu})
        context.update({'user_action': 'delete'})
    except MenuItem.DoesNotExist as e:
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        frame = inspect.currentframe()
        context.update({'error_django': str(e)})
        filename = inspect.getframeinfo(frame).filename
        linenumber = inspect.getframeinfo(frame).lineno
        context.update({'error_msg': 'Unknown error in ' + filename + ' in line ' + str(linenumber)})
        return render(request, 'simplewiki/error.html', context)

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

def handle_section_create(request: WSGIRequest, context: dict) -> HttpResponse:
    """
    Handle Section Create will check the data, sent by the user via the form via a POST
    request and then store it. This function creates a new model object and stores it.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template

    Returns:
        HttpResponse: Returns the template and context to render
    """

    # if do create operation
    if request.POST['confirm_create'] == '1':
        newSectionItem = SectionItem()

        try:
            newSectionItem.title = request.POST['title']
            newSectionItem.menu_path = request.POST['menu_path']
            newSectionItem.index = request.POST['index']
            newSectionItem.icon = request.POST['icon']
            newSectionItem.content = request.POST['content']
        except (KeyError, ValueError, TypeError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)

        try:
            newSectionItem.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
                
        return redirect('simplewiki:admin_sections')
    # if cancel create operation
    else:
        return redirect('simplewiki:admin_sections')

def handle_section_edit(request: WSGIRequest, context: dict, edit: str) -> HttpResponse:
    """
    Handle Sections Edit will check the data, sent by the user via the form via a POST
    request and then store it. This function requests an existing model object and 
    overwrites it.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template
        edit (str): The GET request's value for "edit"

    Returns:
        HttpResponse: Returns the template and context to render
    """

    # if do edit operation
    if request.POST['confirm_edit'] == '1':
        try:
            selectedSection = SectionItem.objects.get(title=edit)
        except SectionItem.DoesNotExist as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)

        # Check if user changed a value. If they did, save the new one.
        keys = ['title', 'menu_path', 'index', 'icon', 'content']
        for key in keys:
            try:
                if request.POST[key]:
                    setattr(selectedSection, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)

        try:
            selectedSection.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)

        return redirect('simplewiki:admin_sections')
    # if cancel edit operation
    elif request.POST['confirm_edit'] == '0':
        return redirect('simplewiki:admin_sections')

def handle_section_delete(request: WSGIRequest, context: dict, delete: str) -> HttpResponse:
    """
    Handle Section Delete will check the data, sent by the user via the form via a POST
    request and then store it. This function requests an existing model object and 
    deletes it.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template
        delete (str): The GET request's value for "delete"

    Returns:
        HttpResponse: Returns the template and context to render
    """

    # if do delete operation
    if request.POST['confirm_delete'] == '1':
        try:
            selectedSection = SectionItem.objects.get(title=delete)
            selectedSection.delete()
        except (SectionItem.DoesNotExist, ProtectedError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        
        return redirect('simplewiki:admin_sections')
    # if cancel delete operation
    elif request.POST['confirm_delete'] == '0':
        return redirect('simplewiki:admin_sections')

def handle_section_edit_get(request: WSGIRequest, context: dict, edit: str) -> HttpResponse:
    """
    Handle Section Edit Get is the GET request helper function for editing menus. This function does 
    not read the GET value data, but only processes it. It takes the data and sends it via the context 
    to the template.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template
        delete (str): The GET request's value for "edit"

    Returns:
        HttpResponse: Returns the template and context to render
    """

    try:
        selectedSection = SectionItem.objects.get(title=edit)
        context.update({'selectedSection': selectedSection})
    except SectionItem.DoesNotExist as e:
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    
    context.update({'user_action': 'edit'})

def handle_section_delete_get(request: WSGIRequest, context: dict, delete: str) -> HttpResponse:
    """
    Handle Section Delete Get is the GET request helper function for deleting sections. This function does 
    not read the GET value data, but only processes it. It takes the data and sends it via the context 
    to the template.

    Args:
        request (WSGIRequest): The standard django request, passed over from the main view
        context (dict): The context so far, will be updates and send to the template
        delete (str): The GET request's value for "edit"

    Returns:
        HttpResponse: Returns the template and context to render
    """

    try:
        selectedSection = SectionItem.objects.get(title=delete)
        context.update({'selectedSection': selectedSection})
    except SectionItem.DoesNotExist as e:
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    
    context.update({'user_action': 'delete'})

