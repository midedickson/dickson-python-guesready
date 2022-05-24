from rest_framework import serializers
from .models import Rental, Reservation
from django.db.models import Q, Subquery, OuterRef


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    rental_id = serializers.PrimaryKeyRelatedField(
        queryset=Rental.objects.all())
    rental = RentalSerializer(read_only=True)
    previous = serializers.CharField()

    class Meta:
        model = Reservation
        fields = ("id", "name", "rental", "rental_id",
                  "check_in", "check_out", "previous")

    def validate(self, attrs):

        selected_rental = attrs['rental_id']
        print(selected_rental)

        reservation_exists = Reservation.objects.filter(
            Q(rental=selected_rental),

            Q(check_out__gte=attrs['check_in']) &
            Q(
                check_in__lte=attrs['check_in']) |
            Q(check_in=attrs['check_in'])).exists()
        if reservation_exists:
            raise serializers.ValidationError(
                "This rental is already booked between these dates.")
        if attrs['check_in'] > attrs['check_out']:
            raise serializers.ValidationError(
                {"check_out": "Check out date must be after check in date."})
        return super().validate(attrs)
