from django.core.management.base import BaseCommand
from django.utils import timezone

import mistune

from simplewiki.models import Section
from simplewiki.markdown import renderer as sw_renderer

# Command to migrate data from 1.0.x to 1.1.3
class Command(BaseCommand):
    """
    A management command to migrate data for SimpleWiki from version 1.0.x to 1.1.3

    This command handles the migration of section items by adding a user who created it (character name + character id) and at what date
    """

    def handle(self, *args, **kwargs):
        # ANSI escape codes for some colors
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'

        print("===== Sections =====")

        try: 
            all_sections = Section.objects.all()

            markdown = mistune.create_markdown(escape=True, 
                                       renderer=sw_renderer.SimpleWikiRenderer(), 
                                       plugins=['strikethrough', 'url', 'footnotes', 'abbr', 'mark', 'insert', 'superscript', 'subscript', 'table'])

            for section in all_sections:

                section.content = markdown(section.content)

                section.save()

                print(GREEN + "Successfully converted " + section.title + " to HTML!" + RESET)

        except Exception as e:
            print(RED + "Unable to save character, character id and time in existing sections! Error: " + RESET + str(e))