from django.core.management.base import BaseCommand
from django.utils import timezone

from allianceauth.authentication.models import UserProfile
from allianceauth.eveonline.models import EveCharacter

from simplewiki.models import Section

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
            first_user = UserProfile.objects.filter(id=2).first()
            if not first_user:
                print(YELLOW + "Unable to find any EVE characters on this auth -> allianceauth.authentication.models.UserProfile with ID 2 returned NULL. Adding 'Administrator' as author to all sections instead." + RESET)

            section_items = Section.objects.all()

            for section in section_items:
                print("Trying to add " + first_user.main_character.character_name + " (ID: " + str(first_user.main_character.character_id) + ") as author for section '" + section.title + "' with today's date.")
                if section.last_edit == "":
                    if first_user:
                        section.last_edit = first_user.main_character.character_name
                    else: 
                        section.last_edit = "Administrator"
                if not section.last_edit_date:
                    section.last_edit_date = timezone.now().date()
                if not section.last_edit_id:
                    if first_user:
                        section.last_edit_id = first_user.main_character.character_id
                    else:
                        section.last_edit_id = 0

                section.save()
                print("Successfully saved section '" + section.title + "'")

            print(GREEN + "Done migrating data" + RESET)
        except Exception as e:
            print(RED + "Unable to save character, character id and time in existing sections! Error: " + RESET + str(e))