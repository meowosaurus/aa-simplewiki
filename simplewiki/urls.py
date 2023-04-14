"""App URLs"""

from django.urls import path

from simplewiki import views

app_name: str = "simplewiki"

urlpatterns = [
    path("", views.index, name="index"),
    path('<str:menu_name>/', views.dynamic_menus, name='dynamic_menu'),
    
    path("admin/pages/", views.admin_pages, name="admin_pages"),
    path("admin/menu/", views.admin_menu, name="admin_menu"),
]
