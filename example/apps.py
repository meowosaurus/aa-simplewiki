"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Example App
from example import __version__


class ExampleConfig(AppConfig):
    """App Config"""

    name = "example"
    label = "example"
    verbose_name = f"Example App v{__version__}"
