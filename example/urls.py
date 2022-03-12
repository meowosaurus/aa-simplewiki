"""App URLs"""

# Django
from django.urls import path

# AA Example App
from example import views

app_name: str = "example"

urlpatterns = [
    path("", views.index, name="index"),
]
