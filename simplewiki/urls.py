"""App URLs"""

from django.urls import path

from simplewiki import views

app_name: str = "simplewiki"

urlpatterns = [
    # basic_access pages
    path("", views.index, name="index"),
    path('search/', views.search, name='search'),
    path('<str:menu_name>/', views.dynamic_menus, name='dynamic_menu'),
    
    # editor_access pages
    path("editor/menus/", views.editor_menus, name="editor_menus"),
    path("editor/sections/", views.editor_sections, name="editor_sections"),
]
