from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [
    path("<int:pk>", views.room_detail, name="detail"),
    path("search/", views.search, name="search"),
]
# FBV

# urlpatterns = [path("<int:pk>", views.RoomDetail.as_view(), name="detail")]
# CBV
