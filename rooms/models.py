from django.contrib.admin.decorators import register
from django.db import models
from django.urls import reverse
from django.db.models.fields import BLANK_CHOICE_DASH
from django_countries.fields import CountryField
from core import models as core_models


class AbstractItem(core_models.TimeStampedModel):

    """Abstract Item"""

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):

    """RoomType Model Definition"""

    class Meta:
        verbose_name = "Room Type"


class Amenity(AbstractItem):

    """Amenity Model Definition"""

    class Meta:
        verbose_name_plural = "Amenities"


class Facility(AbstractItem):

    """Facility Model Definition"""

    class Meta:
        verbose_name_plural = "Facilities"


class HouseRule(AbstractItem):

    """Facility Model Definition"""

    class Meta:
        verbose_name = "House Rule"


class Photo(core_models.TimeStampedModel):

    """Photo Model Definition"""

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="rooms_photos")
    room = models.ForeignKey("Room", related_name="photos", on_delete=models.CASCADE)

    def __str__(self):
        return self.caption


class Room(core_models.TimeStampedModel):

    """Room Model Definition"""

    name = models.CharField(null=True, max_length=140)
    description = models.TextField(null=True)
    country = CountryField(null=True)
    city = models.CharField(null=True, max_length=80)
    price = models.IntegerField(null=True)
    address = models.CharField(null=True, max_length=140)
    guests = models.IntegerField(
        null=True, help_text="How many people will be staying?"
    )
    beds = models.IntegerField(null=True)
    bedrooms = models.IntegerField(null=True)
    baths = models.IntegerField(null=True)
    check_in = models.TimeField(null=True)
    check_out = models.TimeField(null=True)
    instant_book = models.BooleanField(default=False)
    host = models.ForeignKey(
        "users.User", related_name="rooms", on_delete=models.CASCADE, null=True
    )
    room_type = models.ForeignKey(
        "RoomType", related_name="rooms", on_delete=models.SET_NULL, null=True
    )
    amenities = models.ManyToManyField("Amenity", related_name="rooms", blank=True)
    facilities = models.ManyToManyField("Facility", related_name="rooms", blank=True)
    house_rules = models.ManyToManyField("HouseRule", related_name="rooms", blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        self.city = self.city.title()
        super().save(*args, **kwargs)  # Call the real save() method

    def num_reviews(self):
        return len(self.reviews.all())

    def total_rating(self):
        try:
            all_reviews = self.reviews.all()
            all_ratings = 0
            for review in all_reviews:
                all_ratings += review.rating_average()
            return round(all_ratings / len(all_reviews), 2)
        except ZeroDivisionError:
            return 0

    def first_photo(self):
        (photo,) = self.photos.all()[:1]
        return photo.file.url

    def get_next_four_photos(self):
        photos = self.photos.all()[1:5]
        return photos
