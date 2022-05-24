from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

# Create your models here.


class Reservation(models.Model):
    rental = models.ForeignKey('Rental', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, unique=True)
    check_in = models.DateField()
    check_out = models.DateField()

    class Meta:
        ordering = ('-check_out',)

    def get_queryset(self):
        previous = self.find_previous_reservations()
        return self.objects.annotate(previous=models.Subquery(previous.values('name')[:1]))

    def clean(self) -> None:
        selected_rental = self.rental
        reservation_exists = Reservation.objects.filter(Q(rental=selected_rental),
                                                        Q(check_out__gte=self.check_in) &
                                                        Q(
            check_in__lte=self.check_in) |
            Q(check_in=self.check_in)).exists()
        if reservation_exists:
            raise ValidationError(
                "This rental is already booked between these dates.")
        if self.check_in > self.check_out:
            raise ValidationError(
                {"check_out": "Check out date must be after check in date."})
        return super().clean()

    def __str__(self) -> str:
        return f"{self.name} for {self.rental.name}"


class Rental(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return f"Rental - {self.name}"
