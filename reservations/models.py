from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

# Create your models here.


class PreviousReservationFinder():
    """
    This class is used to find the previous reservation.
    """

    def find_previous_reservations(self):
        """
        Finds the last reservation that was booked before the given reservation.
        """
        other_reservations = Reservation.objects.filter(Q(rental=self.rental),
                                                        ~Q(id=self.id), Q(check_in__lt=self.check_in))
        return other_reservations.first()


class Reservation(models.Model, PreviousReservationFinder):
    rental = models.ForeignKey('Rental', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, unique=True)
    check_in = models.DateField()
    check_out = models.DateField()
    previous = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('-check_out',)

    def get_queryset(self):
        return self.objects.all().select_related('previous')

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
