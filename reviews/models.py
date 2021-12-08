from django.db import models
from django.db.models.deletion import CASCADE
from core import models as core_models


class Review(core_models.TimeStampedModel):

    """Review Model Definition"""

    review = models.TextField()
    cleanliness = models.IntegerField()
    accuracy = models.IntegerField()
    communication = models.IntegerField()
    location = models.IntegerField()
    check_in = models.IntegerField()
    value = models.IntegerField()
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    room = models.ForeignKey("rooms.Room", on_delete=CASCADE)

    def __str__(self):
        return f"{self.review} - {self.room.name}"