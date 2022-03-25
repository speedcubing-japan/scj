from django.core.management.base import BaseCommand
from app.models import Person


class Command(BaseCommand):
    help = "reset wca authorization."

    def add_arguments(self, parser):
        parser.add_argument("--person_id", nargs="?", default=0, type=int)

    def handle(self, *args, **options):
        if options["person_id"] is None or options["person_id"] == 0:
            print("person_id is not assigned.")
            exit()

        person = Person.objects.get(pk=options["person_id"])
        person.wca_id = ""
        person.wca_user_id = 0
        person.wca_email = ""
        person.wca_name = ""
        person.wca_birth_at = None
        person.wca_country_iso2 = ""
        person.wca_access_token = ""
        person.wca_refresh_token = ""
        person.wca_avatar_url = ""
        person.wca_avatar_thumb_url = ""
        person.save(
            update_fields=[
                "wca_id",
                "wca_user_id",
                "wca_email",
                "wca_name",
                "wca_birth_at",
                "wca_country_iso2",
                "wca_access_token",
                "wca_refresh_token",
                "wca_avatar_url",
                "wca_avatar_thumb_url",
                "updated_at",
            ]
        )
