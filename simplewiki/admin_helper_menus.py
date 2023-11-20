import inspect
import re

# Django imports
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

# Custom imports
from .models import *
from . import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

def gen_error_context(context: dict, error_code: str, error_e: Exception) -> dict:
    """
    Handles the unknown Exception error output.

    Args:
        context (dict): The main context for the current request
        error_code (str): The current error code, format "#<number>"
        error_e (Exception): The exception thrown by try-except.
        
    Returns:
        dict: Return the updated context
    """

    context.update({'error_code': '#1014'})
    frame = inspect.currentframe()
    context.update({'error_django': str(str(error_e))})
    filename = inspect.getframeinfo(frame).filename
    context.update({'error_code': "EDITOR_MENU_UNKNOWN_ERROR"})
    context.update({'error_msg': 'Unknown error in ' + filename})
    return context

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
        new_menu = Menu()

        try:
            if Menu.objects.all().count() > 0:
                index = Menu.objects.all().last().id
            else:
                index = 0
            setattr(new_menu, 'index', index)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_ADD_NO_INDEX', e))

        # Fill new_menu with variables and check for errors
        keys = ['title', 'icon']
        for key in keys:
            try:
                setattr(new_menu, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_code': 'EDITOR_MENU_ADD_BAD_KEYS'})
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            except Exception as e:
                return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_ADD_UNKNOWN_KEYS', e))

        try:
            menu_icon = format_icon(request.POST['icon'])
            setattr(new_menu, 'icon', menu_icon)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_ADD_BAD_ICON', e))

        # Take all inputs from the group multiple select and put them in a string, seperated by a comma
        group_string = str()
        
        try:
            groups = request.POST.getlist('group_select')

            if groups == "":
                group_string = None
            else:
                for group_item in groups:
                    group_string += group_item
                    group_string += ","
                group_string = group_string[:-1]
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_ADD_BAD_GROUP', e))

        # Take all inputs from the state multiple select and put them in a string, seperated by a comma
        state_string = str()
        try:
            states = request.POST.getlist('state_select')

            if states == "":
                state_string = None
            else:  
                for state_item in states:
                    state_string += state_item
                    state_string += ","
                state_string = state_string[:-1]
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_ADD_BAD_STATE', e))
        
        # Taking the titel and converting it into a url suitable string
        try:
            new_menu.path = slugify(request.POST['title'])
            new_menu.parent = None
            new_menu.groups = group_string
            new_menu.states = state_string
        except (KeyError, ValueError, TypeError) as e:
                context.update({'error_code': 'EDITOR_MENU_TITLE_BAD_URL'})
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
        except Exception as e:
                return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_ADD_TITLE_URL_UNKNOWN', e))
                
        # Save new_menu and check for errors
        try:
            new_menu.save()
        except (IntegrityError, ValidationError) as e:
            context.update({'error_code': 'EDITOR_MENU_ERROR_SAVE'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_ADD_SAVE_UNKNOWN', e))
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
            selected_menu = Menu.objects.get(path=edit)
        except Menu.DoesNotExist as e:
            context.update({'error_code': 'EDITOR_MENU_EDIT_NO_MENU'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_EDIT_BAD_SELECTED_MENU', e))

        # Fill selected_menu with new variables and check for errors
        keys = ['title', 'icon']
        for key in keys:
            try: 
                # Check if user changed a value. If they did, save the new one.
                if request.POST[key]:
                    setattr(selected_menu, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_code': '#1007'})
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            except Exception as e:
                return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_EDIT_BAD_TITLE', e))

        # Check if user changed the icon. If they did, format and save the new one.
        try:
            menu_icon = format_icon(request.POST['icon'])
            setattr(selected_menu, 'icon', menu_icon)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_EDIT_BAD_ICON', e))
        
        # Take all inputs from the group multiple select and put them in a string, seperated by a comma
        try:
            groups = request.POST.getlist('group_select')
            group_string = ""
            for group_item in groups:
                if group_item == "none":
                    group_string = ""
                    break;
                group_string += group_item
                group_string += ","
            group_string = group_string[:-1]
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_EDIT_BAD_GROUP', e))

        # Take all inputs from the state multiple select and put them in a string, seperated by a comma
        try:
            states = request.POST.getlist('state_select')
            state_string = str()
            for state_item in states:
                if state_item == "none":
                    state_string = ""
                    break;
                state_string += state_item
                state_string += ","
            state_string = state_string[:-1]
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_EDIT_BAD_STATE', e))

        # Taking the title and converting it into a url suitable string
        try:
            selected_menu.path = slugify(request.POST['title'])
            selected_menu.groups = group_string
            selected_menu.states = state_string
        except (KeyError, ValueError, TypeError) as e:
            context.update({'error_code': 'EDITOR_MENU_EDIT_BAD_TITLE'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_EDIT_BAD_TITLE_UNKNOWN', e))

        # Save selected_menu and check for errors
        try:
            selected_menu.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_code': 'EDITOR_MENU_EDIT_SAVE'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_EDIT_SAVE_UNKNOWN', e))
                
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
            selected_menu = Menu.objects.get(path=delete)
            selected_menu.delete()
        except (Menu.DoesNotExist, ProtectedError) as e:
            context.update({'error_code': 'EDITOR_MENU_DELETE_404_PROTECTED'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki:error.html', gen_error_context(context, 'EDITOR_MENU_DELETE_UNKNOWN', e))
                
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
        selected_menu = Menu.objects.get(path=edit)
        context.update({'selectedMenu': selected_menu})
        context.update({'user_action': 'edit'})
    except Menu.DoesNotExist as e:
        context.update({'error_code': 'EDITOR_MENU_EDIT_LOAD_FORM'})
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_EDIT_LOAD_FORM_UNKNOWN', e))
    
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
        selected_menu = Menu.objects.get(path=delete)
        context.update({'selectedMenu': selected_menu})
        context.update({'user_action': 'delete'})
    except Menu.DoesNotExist as e:
        context.update({'error_code': 'EDITOR_MENU_DELETE_LOAD_FORM'})
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_MENU_DELETE_LOAD_FORM_UNKNOWN', e))

def format_icon(icon: str) -> str:
    """
    Formats the icon string to match the expected format for Font Awesome icons.

    Args:
        icon (str): The icon string to format.

    Returns:
        str: The formatted icon string.
    """
    try:
        if len(icon) > 0:
            pattern = re.compile(r'^<i class="fas fa-(.*?)"></i>$')
            if pattern.match(icon):
                icon = "fas fa-" + pattern.match(icon).group(1)
            elif not "fas" in icon:
                if not "fa-" in icon:
                    icon = "fas fa-" + icon
                else:
                    icon = "fas " + icon

        return icon
    except Exception as e:
        logger_msg = f'Unable to convert {icon} into "fas fa-<name>" format, proceeding without it.'
        logger.info(logger_msg)

        return ""