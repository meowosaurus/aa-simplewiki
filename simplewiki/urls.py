"""App URLs"""

from django.urls import path

from simplewiki import views

app_name: str = "simplewiki"

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', views.search, name='search'),
    path('<str:menu_name>/', views.dynamic_menus, name='dynamic_menu'),

    
    path("admin/menus/", views.admin_menu, name="admin_menus"),
    path("admin/sections/", views.admin_pages, name="admin_sections"),
]
