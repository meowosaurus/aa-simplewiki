"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import MenuItem, SectionItem


@login_required
@permission_required("simplewiki.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    menu_items = MenuItem.objects.all()
    context = {'menu_items': menu_items}

    # Show the first wiki page 
    if menu_items.count() > 0:
        return redirect('simplewiki:dynamic_menu', menu_items.order_by('index').first())
    # Show a default "create your first page.." error page
    else:
        return render(request, "simplewiki/index.html", context)

@login_required
@permission_required("simplewiki.basic_access")
def dynamic_menus(request, menu_name):
    """
    Dynamic Page view
    :param request:
    :return:
    """
    menuNavItem = get_object_or_404(MenuItem, name=menu_name)
    allMenuItems = MenuItem.objects.all().order_by('index')

    # Order all menus by their index to display them from left to right from low to hight
    filtered_pages = SectionItem.objects.filter(menu_name=menu_name).order_by('index')
    
    return render(request, 'simplewiki/dynamic_page.html', {'menuNavItem': menuNavItem, 'menu_items': allMenuItems, 'filtered_pages': filtered_pages})

@login_required
@permission_required("simplewiki.basic_access")
def admin_pages(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    return render(request, "simplewiki/admin_pages.html")

@login_required
@permission_required("simplewiki.basic_access")
def admin_menu(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    return render(request, "simplewiki/admin_menu.html")

