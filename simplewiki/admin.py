"""Admin models"""

# Django
from django.contrib import admin  # noqa: F401
from .models import *

# Register your models here.
admin.site.register(Menu)
admin.site.register(Section)

admin.site.register(MenuItem)

admin.site.register(SectionItem)
