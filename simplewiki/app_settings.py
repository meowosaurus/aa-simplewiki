"""App Settings"""

# Django
from django.conf import settings

# put your app settings here

simplewiki_display_page_contents = getattr(settings, "SIMPLEWIKI_DISPLAY_PAGE_CONTENTS", True)
