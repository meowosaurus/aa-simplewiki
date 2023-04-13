"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import MenuItem, PageItem


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

    return render(request, "simplewiki/index.html", context)

def dynamic_menus(request, menu_name):
    """
    Dynamic Page view
    :param request:
    :return:
    """
    menuNavItem = get_object_or_404(MenuItem, name=menu_name)
    allMenuItems = MenuItem.objects.all().order_by('index')

    filtered_pages = PageItem.objects.filter(menu_name=menu_name).order_by('index')
    
    return render(request, 'simplewiki/dynamic_page.html', {'menuNavItem': menuNavItem, 'menu_items': allMenuItems, 'filtered_pages': filtered_pages})

def admin_pages(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    return render(request, "simplewiki/admin_pages.html")

def admin_menu(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    return render(request, "simplewiki/admin_menu.html")

