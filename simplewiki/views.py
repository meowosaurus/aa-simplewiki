"""App Views"""

# Django
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

from .models import MenuItem, SectionItem

### Helper Functions ###

# Standard context for a normal view, required by base.html
def genContext(request):

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

# Check if the requester has a specific group
def checkGroup(request, group):
    srp_group = Group.objects.get(name='srp')

    return srp_group in request.user.groups.all()

### User Views ###

@login_required
@permission_required("simplewiki.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
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
def dynamic_menus(request, menu_name):
    """
    Dynamic Page view
    :param request:
    :return:
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
    Search Menu view
    :param request:
    :return:
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

    return render(request, "simplewiki/search.html", context)

### Admin Views ###

@login_required
@permission_required("simplewiki.editor")
def admin_menus(request: WSGIRequest) -> HttpResponse:
    """
    Admin Menu view
    :param request:
    :return:
    """

    context = genContext(request)

    create = request.GET.get('create')
    edit = request.GET.get('edit')
    delete = request.GET.get('delete')

    # Used to update values inside the model
    if request.method == 'POST':

        if create:
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
                    except Exception as e:
                        context.update({'error_django': str(e)})
                        return render(request, 'simplewiki/error.html', context)
                    
                # Taking the titel and converting it into a url suitable string
                newMenu.path = slugify(request.POST['title'])
                
                # Save newMenu and check for errors
                try:
                    newMenu.save()
                except Exception as e:
                    context.update({'error_django': str(e)})
                    return render(request, 'simplewiki/error.html', context)

                return redirect("simplewiki:admin_menus")
            else:
                return redirect("simplewiki:admin_menus")

        # If If edit GET request is still available
        if edit:
            # If do edit operation
            if request.POST['confirm_edit'] == '1':
                try:
                    selectedMenu = MenuItem.objects.get(path=edit)
                except MenuItem.DoesNotExist as e:
                    context.update({'error_django': str(e)})
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
                
                # Taking the titel and converting it into a url suitable string
                selectedMenu.path = slugify(request.POST['title'])

                # Save selectedMenu and check for errors
                try:
                    selectedMenu.save()
                except (ValidationError, IntegrityError) as e:
                    context.update({'error_django': str(e)})
                    return render(request, 'simplewiki/error.html', context)
                
                return redirect("simplewiki:admin_menus")
            # If cancel edit operation
            elif request.POST['confirm_edit'] == '0':
                return redirect("simplewiki:admin_menus")
        
        # If delete GET request is still available
        if delete:
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
    # Used to determine which button the user clicked on to load the correct form
    elif request.method == 'GET':
        if create:
            context.update({'user_action': 'create'})
        elif edit:
            try:
                selectedMenu = MenuItem.objects.get(path=edit)
                context.update({'selectedMenu': selectedMenu})
                context.update({'user_action': 'edit'})
            except MenuItem.DoesNotExist as e:
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
        elif delete:
            try:
                selectedMenu = MenuItem.objects.get(path=delete)
                context.update({'selectedMenu': selectedMenu})
                context.update({'user_action': 'delete'})
            except MenuItem.DoesNotExist as e:
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
        else:
            context.update({'user_action': 'none'})

    return render(request, "simplewiki/admin/admin_menus.html", context)

@login_required
@permission_required("simplewiki.editor")
def admin_sections(request: WSGIRequest) -> HttpResponse:
    """
    Admin sections view
    :param request:
    :return:
    """

    context = genContext(request)

    #return admin_section_view(request, context)

    create = request.GET.get('create')
    edit = request.GET.get('edit')
    delete = request.GET.get('delete')

    if request.method == 'POST':
        if create:
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
        if edit:
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
        if delete:
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

    # Used to determine which button the user clicked on to load the correct form
    if request.method == 'GET':
        if create:
            context.update({'user_action': 'create'})
        elif edit:
            try:
                selectedSection = SectionItem.objects.get(title=edit)
                context.update({'selectedSection': selectedSection})
            except SectionItem.DoesNotExist as e:
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            context.update({'user_action': 'edit'})
        elif delete:
            try:
                selectedSection = SectionItem.objects.get(title=delete)
                context.update({'selectedSection': selectedSection})
            except SectionItem.DoesNotExist as e:
                context.update({'error_django': str(e)})
                return render(request, 'simplewiki/error.html', context)
            context.update({'user_action': 'delete'})
        else:
            context.update({'user_action': 'none'})

    return render(request, "simplewiki/admin/admin_sections.html", context)

