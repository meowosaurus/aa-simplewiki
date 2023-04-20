import inspect

# Django imports
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

# Custom imports
from .models import MenuItem, SectionItem

def create_new_menu(request: WSGIRequest, context: dict) -> HttpResponse:
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
        new_menu = MenuItem()

        # Fill new_menu with variables and check for errors
        keys = ['index', 'title', 'icon', 'groups']
        for key in keys:
            try:
                if key == 'index':
                    setattr(new_menu, key, int(request.POST[key]))
                else:
                    setattr(new_menu, key, request.POST[key])
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
        try:
            new_menu.path = slugify(request.POST['title'])
            new_menu.parent = request.POST['parent']
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
                
        # Save new_menu and check for errors
        try:
            new_menu.save()
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
        return redirect("simplewiki:editor_menus")
    else:
        return redirect("simplewiki:editor_menus")
    
def edit_existing_menu(request: WSGIRequest, context: dict, edit: str) -> HttpResponse:
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
            selected_menu = MenuItem.objects.get(path=edit)
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

        # Fill selected_menu with new variables and check for errors
        keys = ['index', 'title', 'icon', 'groups']
        for key in keys:
            try: 
                # Check if user changed a value. If they did, save the new one.
                if request.POST[key]:
                    if key == 'index':
                        setattr(selected_menu, key, int(request.POST[key]))
                    else:
                        setattr(selected_menu, key, request.POST[key])
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
        try:
            selected_menu.path = slugify(request.POST['title'])
            selected_menu.parent = request.POST['parent']
            selected_menu.groups = request.POST['groups']
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

        # Save selected_menu and check for errors
        try:
            selected_menu.save()
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
                
        return redirect("simplewiki:editor_menus")
    # If cancel edit operation
    elif request.POST['confirm_edit'] == '0':
        return redirect("simplewiki:editor_menus")

def delete_existing_menu(request: WSGIRequest, context: dict, delete: str) -> HttpResponse:
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
            selected_menu = MenuItem.objects.get(path=delete)
            selected_menu.delete()
        except (MenuItem.DoesNotExist, ProtectedError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
                
        return redirect("simplewiki:editor_menus")
    # If cancel delete operation
    elif request.POST['confirm_delete'] == '0':
        return redirect("simplewiki:editor_menus")

def load_menu_edit_form(request: WSGIRequest, context: dict, edit: str) -> HttpResponse:
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
        selected_menu = MenuItem.objects.get(path=edit)
        context.update({'selectedMenu': selected_menu})
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
    
def load_menu_delete_form(request: WSGIRequest, context: dict, delete: str) -> HttpResponse:
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
        selected_menu = MenuItem.objects.get(path=delete)
        context.update({'selectedMenu': selected_menu})
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
    
### SECTION ###

def create_new_section(request: WSGIRequest, context: dict) -> HttpResponse:
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
        new_section = SectionItem()

        try:
            new_section.title = request.POST['title']
            new_section.menu_path = request.POST['menu_path']
            new_section.index = request.POST['index']
            new_section.icon = request.POST['icon']
            new_section.content = request.POST['content']
        except (KeyError, ValueError, TypeError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)

        try:
            new_section.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
                
        return redirect('simplewiki:editor_sections')
    # if cancel create operation
    else:
        return redirect('simplewiki:editor_sections')

def edit_existing_section(request: WSGIRequest, context: dict, edit: str) -> HttpResponse:
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
            selected_section = SectionItem.objects.get(title=edit)
        except SectionItem.DoesNotExist as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)

        # Check if user changed a value. If they did, save the new one.
        keys = ['title', 'menu_path', 'index', 'icon', 'content']
        for key in keys:
            try:
                if request.POST[key]:
                    setattr(selected_section, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)

        try:
            selected_section.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)

        return redirect('simplewiki:editor_sections')
    # if cancel edit operation
    elif request.POST['confirm_edit'] == '0':
        return redirect('simplewiki:editor_sections')

def delete_existing_section(request: WSGIRequest, context: dict, delete: str) -> HttpResponse:
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
            selected_section = SectionItem.objects.get(title=delete)
            selected_section.delete()
        except (SectionItem.DoesNotExist, ProtectedError) as e:
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        
        return redirect('simplewiki:editor_sections')
    # if cancel delete operation
    elif request.POST['confirm_delete'] == '0':
        return redirect('simplewiki:editor_sections')

def load_section_edit_form(request: WSGIRequest, context: dict, edit: str) -> HttpResponse:
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
        selected_section = SectionItem.objects.get(title=edit)
        context.update({'selectedSection': selected_section})
    except SectionItem.DoesNotExist as e:
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    
    context.update({'user_action': 'edit'})

def load_section_delete_form(request: WSGIRequest, context: dict, delete: str) -> HttpResponse:
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
        selected_section = SectionItem.objects.get(title=delete)
        context.update({'selectedSection': selected_section})
    except SectionItem.DoesNotExist as e:
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    
    context.update({'user_action': 'delete'})



