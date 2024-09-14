"""Admin models.

This module contains the admin models for the SimpleWiki app.
"""

# Django
from django.contrib import admin  # noqa: F401
from .models import *

# v1.1
admin.site.register(Menu)
admin.site.register(Section)

# v1.0
#admin.site.register(MenuItem)
#admin.site.register(SectionItem)
