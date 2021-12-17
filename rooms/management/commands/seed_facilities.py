from django.core.management.base import BaseCommand
from rooms.models import Facility


class Command(BaseCommand):

    help = "This command creates facilities"

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Create facilities..",
        )

    # python manage.py seed_amenities --seed

    def handle(self, *args, **options):
        facilities = [
            "Private entrance",
            "Paid parking on premises",
            "Paid parking off premises",
            "Elevator",
            "Parking",
            "Gym",
        ]
        a = 0
        for f in facilities:
            if not Facility.objects.filter(name=f):  # 중복체크
                a += 1
                Facility.objects.create(name=f)
        self.stdout.write(self.style.SUCCESS(f"{a} facilities created!"))
