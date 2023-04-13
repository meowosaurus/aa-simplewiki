"""Admin models"""

# Django
from django.contrib import admin  # noqa: F401
from .models import MenuItem
from .models import SectionItem

# Register your models here.
admin.site.register(MenuItem)

admin.site.register(SectionItem)


