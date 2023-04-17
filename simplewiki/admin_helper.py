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
            selectedMenu = MenuItem.objects.get(path=delete)
            selectedMenu.delete()
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
            selectedSection = SectionItem.objects.get(title=delete)
            selectedSection.delete()
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
        selectedSection = SectionItem.objects.get(title=edit)
        context.update({'selectedSection': selectedSection})
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
        selectedSection = SectionItem.objects.get(title=delete)
        context.update({'selectedSection': selectedSection})
    except SectionItem.DoesNotExist as e:
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    
    context.update({'user_action': 'delete'})



