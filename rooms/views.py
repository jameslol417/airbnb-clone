from django.core import paginator
from django.shortcuts import render  # ,redirect
from django.http import Http404

# DetailView FBV

from django.core.paginator import Paginator  # ,EmptyPage

# HomeView FBV
# -------------Function Based View------------------
from django.views.generic import ListView  # , DetailView -> CBV, View ---->CBV forms

# --------------Class Based View---------------------
from django_countries import countries
from . import models, forms


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

    country = request.GET.get("country")

    if country:

        form = forms.SearchForm(request.GET)

        if form.is_valid():
            city = form.cleaned_data.get("city")
            country = form.cleaned_data.get("country")
            room_type = form.cleaned_data.get("room_type")
            price = form.cleaned_data.get("price")
            guests = form.cleaned_data.get("guests")
            bedrooms = form.cleaned_data.get("bedrooms")
            beds = form.cleaned_data.get("beds")
            baths = form.cleaned_data.get("baths")
            instant_book = form.cleaned_data.get("intsant_book")
            superhost = form.cleaned_data.get("superhost")
            amenities = form.cleaned_data.get("amenities")
            facilities = form.cleaned_data.get("facilities")

            filter_args = {}

            if city != "Anywhere":
                filter_args["city__startswith"] = city

            filter_args["country"] = country

            if room_type is not None:
                filter_args["room_type"] = room_type

            if price is not None:
                filter_args["price__lte"] = price

            if guests is not None:
                filter_args["guests__gte"] = guests

            if bedrooms is not None:
                filter_args["bedrooms__gte"] = bedrooms

            if beds is not None:
                filter_args["beds__gte"] = beds

            if baths is not None:
                filter_args["baths__gte"] = baths

            if instant_book is True:
                filter_args["instant_book"] = True

            if superhost is True:
                filter_args["host__superhost"] = True

            rooms = models.Room.objects.filter(**filter_args)

            for amenity in amenities:
                rooms = rooms.filter(amenities=amenity)

            for facility in facilities:
                rooms = rooms.filter(facilities=facility)

            qs = rooms.order_by("created")

            paginator = Paginator(qs, 10, orphans=5)

            page = request.GET.get("page", 1)

            p_rooms = paginator.page(int(page))

            # method of pagination is for CBV

            return render(
                request,
                "rooms/search.html",
                {"form": form, "rooms": p_rooms},
            )

    else:
        form = forms.SearchForm()

    return render(
        request,
        "rooms/search.html",
        {
            "form": form,
        },
    )


# class SearchView(View):

#     def get(self,request):
# everything same as FBV
# ----------------CBV----------------------
