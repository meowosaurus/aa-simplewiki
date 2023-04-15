"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import MenuItem, SectionItem

# Standard context for a normal view, required by base.html
def genContext(request):

    menu_items = MenuItem.objects.all()
    section_items = SectionItem.objects.all()

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
        context.update({'searchResults': searchResults})

    return render(request, "simplewiki/search.html", context)

### Admin ###

@login_required
@permission_required("simplewiki.editor")
def admin_menu(request: WSGIRequest) -> HttpResponse:
    """
    Admin Menu view
    :param request:
    :return:
    """

    return render(request, "simplewiki/admin_menus.html", genContext(request))

@login_required
@permission_required("simplewiki.editor")
def admin_pages(request: WSGIRequest) -> HttpResponse:
    """
    Admin pages view
    :param request:
    :return:
    """

    return render(request, "simplewiki/admin_sections.html", genContext(request))

