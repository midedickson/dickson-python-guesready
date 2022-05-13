from rest_framework import serializers
from .models import Rental, Reservation
from django.db.models import Q


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    previous = serializers.SerializerMethodField()
    rental_id = serializers.PrimaryKeyRelatedField(
        queryset=Rental.objects.all())
    rental = RentalSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'

    def get_previous(self, obj):
        return ReservationSerializer(obj.find_previous_reservations()).data if obj.find_previous_reservations() else None

    def create(self, validated_data):
        rental = validated_data.pop('rental_id')
        validated_data["rental"] = rental
        return Reservation.objects.create(**validated_data)

    def validate(self, attrs):

        selected_rental = attrs['rental_id']
        print(selected_rental)

        reservation_exists = Reservation.objects.filter(
            rental=selected_rental).filter(Q(check_in=attrs['check_in']) | Q(check_out__gte=attrs['check_in'])).exists()
        if reservation_exists:
            raise serializers.ValidationError(
                "This rental is already booked between these dates.")
        if attrs['check_in'] > attrs['check_out']:
            raise serializers.ValidationError(
                {"check_out": "Check out date must be after check in date."})
        return super().validate(attrs)
