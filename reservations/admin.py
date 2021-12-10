from django.contrib import admin
from django.utils import timezone
from . import models
import reservations


class ProgressListFilter(admin.SimpleListFilter):
    title = "In Progress"  # 필터에 By .... 에 들어갈 녀석을 적음
    parameter_name = "in_progress"  # 필터링할 녀석

    def lookups(self, request, model_admin):
        return (
            ("True", "True"),
            ("False", "False"),
        )

    def queryset(self, request, queryset):
        now = timezone.now().date()
        if self.value() == "True":
            return queryset.filter(check_in__lte=now, check_out__gte=now)
        elif self.value() == "False":
            return queryset.exclude(check_in__lte=now, check_out__gte=now)


class FinishedListFilter(admin.SimpleListFilter, admin.ModelAdmin):
    title = "Is Finished"  # 필터에 By .... 에 들어갈 녀석을 적음
    parameter_name = "is_finished"  # 필터링할 녀석

    def lookups(self, request, model_admin):
        return (
            ("True", "True"),
            ("False", "False"),
        )

    def queryset(self, request, queryset):
        now = timezone.now().date()
        if self.value() == "True":
            return queryset.filter(check_out__lt=now)
        elif self.value() == "False":
            return queryset.exclude(check_out__lt=now)


@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):

    """Reservation Admin Definition"""

    list_display = (
        "room",
        "status",
        "check_in",
        "check_out",
        "guest",
        "in_progress",
        "is_finished",
    )

    list_filter = ("status", ProgressListFilter, FinishedListFilter)
