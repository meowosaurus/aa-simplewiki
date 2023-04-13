"""App Configuration"""

# Django
from django.apps import AppConfig

# AA simplewiki App
from simplewiki import __version__


class simplewikiConfig(AppConfig):
    """App Config"""

    name = "simplewiki"
    label = "simplewiki"
    verbose_name = f"simplewiki App v{__version__}"
