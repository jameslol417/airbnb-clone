from re import template
from django.http import Http404

# from django.core import paginator
from django.shortcuts import render, redirect, reverse

# DetailView FBV

from django.core.paginator import Paginator  # ,EmptyPage
from django.contrib.auth.decorators import login_required  # decorators!
from django.contrib import messages

# HomeView FBV
# -------------Function Based View------------------
from django.views.generic import (
    ListView,
    UpdateView,
    DetailView,
    FormView,
)  # CreateView is not used due to need to upload photos

# View ---->CBV forms
from django.contrib.messages.views import SuccessMessageMixin
from users import mixins as user_mixins

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
    paginate_by = 12
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"


def room_detail(request, pk):
    try:
        room = models.Room.objects.get(pk=pk)
        return render(request, "rooms/room_detail.html", {"room": room})
    except models.Room.DoesNotExist:
        # return redirect(reverse("core:home"))
        raise Http404()


# class RoomDetail(DetailView):

#     """RoomDetail Definition"""

#     model = models.Room


# --------------CBV----------------


def search(request):

    # city = request.GET.get("city")
    # if city:
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
            instant_book = form.cleaned_data.get("instant_book")
            superhost = form.cleaned_data.get("superhost")
            amenities = form.cleaned_data.get("amenities")
            facilities = form.cleaned_data.get("facilities")

            filter_args = {}

            if city != "Anywhere":
                filter_args["city__istartswith"] = city

            if country is not None:
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


class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):
    model = models.Room
    template_name = "rooms/room_edit.html"
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )

    def get_object(self, queryset=None):
        room = super().get_object(queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


class RoomPhotosView(user_mixins.LoggedInOnlyView, DetailView):

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Can't delete that photo")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo Deleted")
        return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.Photo
    template_name = "rooms/photo_edit.html"
    pk_url_kwarg = "photo_pk"
    success_message = "Photo Updated"
    fields = ("caption",)

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoView(
    user_mixins.LoggedInOnlyView, FormView
):  # SuccessMessageMixin and form_valid collide

    model = models.Photo
    template_name = "rooms/photo_create.html"
    fields = ("caption", "file")
    form_class = forms.CreatePhotoForm

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("rooms:photos", kwargs={"pk": pk}))
