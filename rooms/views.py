from django.shortcuts import render  # ,redirect
from django.http import Http404

# DetailView FBV

# from django.core.paginator import EmptyPage, Paginator

# HomeView FBV
# -------------Function Based View------------------
from django.views.generic import ListView  # , DetailView -> CBV

# --------------Class Based View---------------------
from django_countries import countries
from . import models


# def all_rooms(request):
#     page = request.GET.get("page", 1)
#     room_list = models.Room.objects.all()
#     paginator = Paginator(room_list, 10, orphans=5)
#     try:
#         rooms = paginator.page(int(page))
#         return render(request, "rooms/home.html", {"pages": rooms})
#     except EmptyPage:
#         return redirect("/")
# -------------------------------------------------------------------


class HomeView(ListView):

    """HomeView Definition"""

    model = models.Room
    paginate_by = 10
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"


def room_detail(request, pk):
    try:
        room = models.Room.objects.get(pk=pk)
        return render(request, "rooms/detail.html", {"room": room})
    except models.Room.DoesNotExist:
        # return redirect(reverse("core:home"))
        raise Http404()


# class RoomDetail(DetailView):

#     """RoomDetail Definition"""

#     model = models.Room


# --------------CBV----------------


def search(request):
    city = request.GET.get("city", "Anywhere")
    city = str.capitalize(city)
    room_types = models.RoomType.objects.all()
    country = request.GET.get("country", "KR")
    room_type = int(request.GET.get("room_type", 0))

    form = {
        "city": city,
        "s_country": country,
        "s_room_type": room_type,
    }

    choices = {
        "countries": countries,
        "room_types": room_types,
    }

    return render(
        request,
        "rooms/search.html",
        {**form, **choices},
    )
