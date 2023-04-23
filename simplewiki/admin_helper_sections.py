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
from .models import SectionItem

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

    context.update({'error_code': '#1014'})
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
        new_section = SectionItem()

        try:
            new_section.title = request.POST['title']
            new_section.menu_path = request.POST['menu_path']
            new_section.index = request.POST['index']
            new_section.icon = request.POST['icon']
            new_section.content = request.POST['content']
        except (KeyError, ValueError, TypeError) as e:
            context.update({'error_code': '#1014'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1014', e))

        try:
            new_section.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_code': '#1014'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1014', e))
                
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
            context.update({'error_code': '#1015'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)

        # Check if user changed a value. If they did, save the new one.
        keys = ['title', 'menu_path', 'index', 'icon', 'content']
        for key in keys:
            try:
                if request.POST[key]:
                    setattr(selected_section, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_code': '#1015'})
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            except Exception as e:
                return render(request, 'simplewiki/error.html', gen_error_context(context, '#1015', e))

        try:
            selected_section.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_code': '#1016'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1016', e))

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
            context.update({'error_code': '#1017'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1017', e))
        
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
        context.update({'error_code': '#1018'})
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        return render(request, 'simplewiki/error.html', gen_error_context(context, '#1018', e))
    
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
        context.update({'error_code': '#1018'})
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        return render(request, 'simplewiki/error.html', gen_error_context(context, '#1014', e))
    
    context.update({'user_action': 'delete'})



