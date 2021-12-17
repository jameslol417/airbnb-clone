import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from rooms import models as room_models
from users import models as user_models


class Command(BaseCommand):

    help = "This command creates rooms"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            default=2,
            type=int,
            help="How many rooms do you want to create?",
        )

    # python manage.py seed_amenities --seed

    def handle(self, *args, **options):
        # make proper seed later

        number = options.get("number")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        room_types = room_models.RoomType.objects.all()
        seeder.add_entity(
            room_models.Room,
            number,
            {
                "name": lambda x: seeder.faker.company(),
                "address": lambda x: seeder.faker.address(),
                "price": lambda x: random.randint(0, 4000),
                "guests": lambda x: random.randint(1, 40),
                "beds": lambda x: random.randint(1, 40),
                "bedrooms": lambda x: random.randint(1, 20),
                "baths": lambda x: random.randint(1, 20),
                "host": lambda x: random.choice(all_users),
                "room_type": lambda x: random.choice(room_types),
            },
        )
        pk_list = seeder.execute()
        created_clean = flatten(list(pk_list.values()))
        amenities = room_models.Amenity.objects.all()
        facilites = room_models.Facility.objects.all()
        rules = room_models.HouseRule.objects.all()
        for pk in created_clean:
            room = room_models.Room.objects.get(pk=pk)
            for i in range(3, random.randint(10, 30)):
                room_models.Photo.objects.create(
                    caption=seeder.faker.sentence,
                    room=room,
                    file=f"rooms_photos/{random.randint(1,31)}.webp",
                )
            for a in amenities:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.amenities.add(a)
            for f in facilites:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.facilities.add(f)
            for r in rules:
                magic_number = random.randint(0, 15)
                if magic_number % 2 == 0:
                    room.house_rules.add(r)

        self.stdout.write(self.style.SUCCESS(f"{number} rooms created!"))
