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
from .models import MenuItem

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
    context.update({'error_code': error_code})
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
        new_menu = MenuItem()

        # Fill new_menu with variables and check for errors
        keys = ['index', 'title', 'icon']
        for key in keys:
            try:
                if key == 'index':
                    setattr(new_menu, key, int(request.POST[key]))
                else:
                    setattr(new_menu, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_code': '#1003'})
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            except Exception as e:
                return render(request, 'simplewiki/error.html', gen_error_context(context, '#1003', e))

        # Take all inputs from the group multiple select and put them in a string, seperated by a comma
        #group_string = ""
        group_string = str()
        
        try:
            
            groups = request.POST.getlist('group_select')

            for group_item in groups:
                group_string += group_item
                group_string += ","
            group_string = group_string[:-1]
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1003', e))
        
        # Taking the titel and converting it into a url suitable string
        try:
            new_menu.path = slugify(request.POST['title'])
            if request.POST['parent_select'] == "none":
                new_menu.parent = ""
            else:
                new_menu.parent = request.POST['parent_select']
            new_menu.groups = group_string
        except (KeyError, ValueError, TypeError) as e:
                context.update({'error_code': '#1004'})
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
        except Exception as e:
                return render(request, 'simplewiki/error.html', gen_error_context(context, '#1004', e))
                
        # Save new_menu and check for errors
        try:
            new_menu.save()
        except (IntegrityError, ValidationError) as e:
            context.update({'error_code': '#1005'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1005', e))
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
            context.update({'error_code': '#1006'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1006', e))

        # Fill selected_menu with new variables and check for errors
        keys = ['index', 'title', 'icon']
        for key in keys:
            try: 
                # Check if user changed a value. If they did, save the new one.
                if request.POST[key]:
                    if key == 'index':
                        setattr(selected_menu, key, int(request.POST[key]))
                    else:
                        setattr(selected_menu, key, request.POST[key])
            except (KeyError, ValueError, TypeError) as e:
                context.update({'error_code': '#1007'})
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            except Exception as e:
                return render(request, 'simplewiki/error.html', gen_error_context(context, '#1007', e))
        
        # ToDo Error 'groups'
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
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1008', e))

        # Taking the titel and converting it into a url suitable string
        try:
            selected_menu.path = slugify(request.POST['title'])
            if request.POST['parent_select'] == "none":
                selected_menu.parent = ""
            else:
                selected_menu.parent = request.POST['parent_select']
            selected_menu.groups = group_string
        except (KeyError, ValueError, TypeError) as e:
            context.update({'error_code': '#1009'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1009', e))

        # Save selected_menu and check for errors
        try:
            selected_menu.save()
        except (ValidationError, IntegrityError) as e:
            context.update({'error_code': '#1010'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki/error.html', gen_error_context(context, '#1010', e))
                
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
            context.update({'error_code': '#1011'})
            context.update({'error_django': str(e)})
            return render(request, 'simplewiki/error.html', context)
        except Exception as e:
            return render(request, 'simplewiki:error.html', gen_error_context(context, '#1011', e))
                
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
        context.update({'error_code': '#1012'})
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        return render(request, 'simplewiki/error.html', gen_error_context(context, '#1012', e))
    
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
        context.update({'error_code': '#1013'})
        context.update({'error_django': str(e)})
        return render(request, 'simplewiki/error.html', context)
    except Exception as e:
        return render(request, 'simplewiki/error.html', gen_error_context(context, '#1013', e))