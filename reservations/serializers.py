from rest_framework import serializers
from .models import Rental, Reservation
from django.db.models import Q


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    rental_id = serializers.PrimaryKeyRelatedField(
        queryset=Rental.objects.all())
    rental = RentalSerializer(read_only=True)
    previous = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = '__all__'

    def create(self, validated_data):
        rental = validated_data.pop('rental_id')
        validated_data["rental"] = rental
        reservation = Reservation.objects.create(**validated_data)
        if reservation.find_previous_reservations() is not None:
            reservation.previous = reservation.find_previous_reservations()
            reservation.save()
        return reservation

    def get_previous(self, obj):
        return ReservationSerializer(obj.previous).data if obj.previous else None

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
