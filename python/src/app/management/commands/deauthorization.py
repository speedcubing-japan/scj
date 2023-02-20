from django.core.management.base import BaseCommand
from app.models import Person
from django.conf import settings
import stripe


class Command(BaseCommand):
    help = "deauthorize stripe connect"

    def add_arguments(self, parser):
        parser.add_argument("--person_id", nargs="?", default=0, type=int)

    def handle(self, *args, **options):
        if options["person_id"] is None or options["person_id"] == 0:
            print("person_id is not assigned.")
            exit()

        person = Person.objects.get(pk=options["person_id"])

        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.OAuth.deauthorize(
            client_id=settings.STRIPE_CLIENT_ID, stripe_user_id=person.stripe_user_id
        )

        person.stripe_user_id = ""
        person.save(
            update_fields=[
                "stripe_user_id",
                "updated_at",
            ]
        )
