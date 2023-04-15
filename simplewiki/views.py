"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms
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

    menu_items = MenuItem.objects.all()

    # Show the first wiki page 
    if menu_items.count() > 0:
        return redirect('simplewiki:dynamic_menu', menu_items.order_by('index').first())
    # Show a default "create your first page.." error page
    else:
        return render(request, "simplewiki/index.html", genContext(request))

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
        return render(request, 'simplewiki/group_error.html', context)

@login_required
@permission_required("simplewiki.basic_access") 
def search(request: WSGIRequest) -> HttpResponse:
    """
    Search Menu view
    :param request:
    :return:
    """

    context = genContext(request)

    query = request.GET.get('query')
    if query:
        searchResults = SectionItem.objects.filter(content__icontains=query)
        context.update({'oldQuery': query})
        context.update({'searchResults': searchResults})

    return render(request, "simplewiki/search.html", context)

### Admin Views ###

@login_required
@permission_required("simplewiki.editor")
def admin_menu(request: WSGIRequest) -> HttpResponse:
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

                newMenu.index = request.POST['index']
                newMenu.title = request.POST['title']
                newMenu.icon = request.POST['icon']
                newMenu.path = request.POST['path']
                newMenu.group = request.POST['group']

                newMenu.save()
                return redirect("simplewiki:admin_menus")
            else:
                return redirect("simplewiki:admin_menus")

        # If If edit GET request is still available
        if edit:
            # If do edit operation
            if request.POST['confirm_edit'] == '1':
                selectedMenu = MenuItem.objects.get(path=edit)

                # Check if user changed a value. If they did, save the new one.
                if request.POST['index']:
                    selectedMenu.index = request.POST['index']
                if request.POST['title']:
                    selectedMenu.title = request.POST['title']
                if request.POST['icon']:
                    selectedMenu.icon = request.POST['icon']
                if request.POST['path']:
                    selectedMenu.path = request.POST['path']
                if request.POST['group']:
                    selectedMenu.group = request.POST['group']

                selectedMenu.save()
                return redirect("simplewiki:admin_menus")
            # If cancel edit operation
            elif request.POST['confirm_edit'] == '0':
                return redirect("simplewiki:admin_menus")
        
        # If delete GET request is still available
        if delete:
            # If do delete operation
            if request.POST['confirm_delete'] == '1':
                selectedMenu = MenuItem.objects.get(path=delete)
                selectedMenu.delete()
                return redirect("simplewiki:admin_menus")
            # If cancel delete operation
            elif request.POST['confirm_delete'] == '0':
                return redirect("simplewiki:admin_menus")
    # Used to determine which button the user clicked on to load the correct form
    elif request.method == 'GET':
        if create:
            context.update({'act': 3})
        elif edit:
            selectedMenu = MenuItem.objects.get(path=edit)
            context.update({'selectedMenu': selectedMenu})
            context.update({'act': 1}) # 1 = edit
        elif delete:
            selectedMenu = MenuItem.objects.get(path=delete)
            context.update({'selectedMenu': selectedMenu})
            context.update({'act': 2}) # 2 = delete
        else:
            context.update({'act': 0}) # 0 = nothing, show list

    return render(request, "simplewiki/admin/admin_menus.html", context)

@login_required
@permission_required("simplewiki.editor")
def admin_pages(request: WSGIRequest) -> HttpResponse:
    """
    Admin pages view
    :param request:
    :return:
    """

    context = genContext(request)

    return render(request, "simplewiki/admin/admin_sections.html", context)

