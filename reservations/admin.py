from django.contrib import admin
from .models import Rental, Reservation

# Register your models here.

admin.site.register(Rental)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'rental', 'check_in', 'check_out')
    list_filter = ('rental', 'check_in', 'check_out')
