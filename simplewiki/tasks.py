"""App Tasks"""

# Standard Library
import logging

# Third Party
from celery import shared_task

logger = logging.getLogger(__name__)

# simplewiki Task
@shared_task
def simplewiki_task():
    """simplewiki Task"""

    pass
