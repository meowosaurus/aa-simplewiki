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

# Alliance Auth imports
from allianceauth.services.hooks import get_extension_logger
from allianceauth.authentication.models import UserProfile
from allianceauth.eveonline.models import EveCharacter

# Custom imports
from .models import *

# Logging
from app_utils.logging import LoggerAddTag
from . import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)

def gen_error_context(context: dict, error_code: str, err_e: Exception):
    """
    Handles the unknown Exception error output.

    Args:
        context (dict): The main context for the current request
        error_code (str): The current error code, format "#<number>"
        error_e (Exception): The exception thrown by try-except.
        
    Returns:
        dict: Return the updated context
    """

    context.update({'error_code': 'EDITOR_SECTION_ERROR_UNKNOWN'})
    frame = inspect.currentframe()
    context.update({'error_django': str(str(err_e))})
    filename = inspect.getframeinfo(frame).filename
    context.update({'error_msg': 'Unknown error in ' + filename})
    return context

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
        new_section = Section()

        # Get user who sent the create request
        try:
            user = UserProfile.objects.filter(user=request.user).first()
            new_section.last_edit = user.main_character.character_name
            new_section.last_edit_id = user.main_character.character_id
        except Exception as e:
            logger.error("Unable to find user who tries to create a new section")

        # Check if user changed a value. If they did, save the new one.
        try:
            new_section.title = request.POST['title']
            menu_path = request.POST['menu_path']
            new_section.menu = Menu.objects.get(path=menu_path)
            new_section.icon = format_icon(request.POST['icon'])
            new_section.content = request.POST['content']
        except (KeyError, ValueError, TypeError) as e:
            context.update({'error_code': 'EDITOR_SECTION_CREATE'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_CREATE_UNKNOWN', e))

        # Check if user changed the index. If they did, save the new one.
        try:
            index = request.POST['index']
            if re.match(r'^-?\d+$', index):
                new_section.index = int(request.POST['index'])
            else:
                new_section.index = 0
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_CREATE_INDEX', e))

        # Save the object
        try:
            new_section.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_code': 'EDITOR_SECTION_CREATE_SAVE'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_CREATE_SAVE_UNKNOWN', e))
                
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
        # Get the object
        try:
            selected_section = Section.objects.get(title=edit)
        except Section.DoesNotExist as e:
            context.update({'error_code': 'EDITOR_SECTION_EDIT_GET'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)

        # Get user who tries to edit the section
        try:
            user = UserProfile.objects.filter(user=request.user).first()
            selected_section.last_edit = user.main_character.character_name
            selected_section.last_edit_id = user.main_character.character_id
        except Exception as e:
            logger.error("Unable to find user who tries to edit an existing section")

        # Check if user changed a value. If they did, save the new one.
        keys = ['title', 'icon']
        for key in keys:
            try:
                if request.POST[key]:
                    setattr(selected_section, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_code': 'EDITOR_SECTION_EDIT_VALUES'})
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            except Exception as e:
                return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_EDIT_VALUES_UNKNOWN', e))

        try:
            content = request.POST['content']
            
            content = re.sub(r'aria-expanded="true"', 'aria-expanded="false"', content)
            content = re.sub(r'class="accordion-collapse collapse show"', 'class="accordion-collapse collapse"', content)
            content = re.sub(r'class="accordion-button(?!"collapsed")', 'class="accordion-button collapsed"', content)

            selected_section.content = content
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_EDIT_ICON', e))

        # Check if user changed the icon. If they did, save the new one.
        try:
            setattr(selected_section, 'icon', format_icon(request.POST['icon']))
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_EDIT_ICON', e))

        # Check if user changed the index. If they did, save the new one.
        try:
            index = request.POST['index']
            if re.match(r'^-?\d+$', index):
                selected_section.index = int(request.POST['index'])
            else:
                selected_section.index = 0
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_EDIT_INDEX', e))

        # Check if user changed the menu. If they did, save the new one.
        try:
            menu_path = request.POST['menu_path']
            if menu_path == "":
                selected_section.menu = None
            else:
                selected_section.menu = Menu.objects.get(path=menu_path)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_EDIT_MENU', e))

        # Save the object
        try:
            selected_section.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_code': 'EDITOR_SECTION_EDIT_SAVE'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_EDIT_SAVE_UNKNOWN', e))

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
            selected_section = Section.objects.get(title=delete)
            selected_section.delete()
        except (Section.DoesNotExist, ProtectedError) as e:
            context.update({'error_code': 'EDITOR_SECTION_DELETE'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_DELETE_UNKNOWN', e))
        
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
        selected_section = Section.objects.get(title=edit)
        context.update({'selectedSection': selected_section})
    except Section.DoesNotExist as e:
        context.update({'error_code': 'EDITOR_SECTION_LOAD_EDIT_FORM'})
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_LOAD_EDIT_FORM_UNKNOWN', e))
    
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
        selected_section = Section.objects.get(title=delete)
        context.update({'selectedSection': selected_section})
    except Section.DoesNotExist as e:
        context.update({'error_code': 'EDITOR_SECTION_LOAD_DELETE_FORM'})
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        return render(request, 'simplewiki/error.html', gen_error_context(context, 'EDITOR_SECTION_LOAD_DELETE_FORM_UNKNOWN', e))
    
    context.update({'user_action': 'delete'})

def format_icon(icon: str) -> str:
    """
    Formats the given icon string to match the FontAwesome icon class format.

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

