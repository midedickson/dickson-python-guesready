from http import client
from unicodedata import name
from rest_framework.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from reservations.models import Rental, Reservation
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK

# Create your tests here.


class ReservationTester(APITestCase):
    def setUp(self):
        rental = Rental.objects.create(name='Test Rental')
        Reservation.objects.create(
            rental=rental, name='Test Reservation', check_in='2020-01-01', check_out='2020-01-05')
        Reservation.objects.create(
            rental=rental, name='Test Reservation2', check_in='2020-01-06', check_out='2020-01-10')

    def test_reservation_creation(self):
        rental = Rental.objects.get(name='Test Rental')
        reservation = Reservation.objects.get(name='Test Reservation')

        self.assertEqual(reservation.rental, rental)
        self.assertEqual(reservation.name, 'Test Reservation')
        Reservation.objects.create(
            rental=rental, name='Test 3', check_in='2020-01-01', check_out='2020-01-05')
        self.assertRaisesMessage(
            ValidationError, "This rental is already booked between these dates.")


class ReservationEndpintTester(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse('reservations')
        self.rental = Rental.objects.create(name='Test Rental')
        self.rental2 = Rental.objects.create(name='Test Rental2')

    def test_reservation_creation(self):
        data = {
            'rental_id': self.rental.id,
            'name': 'Create Test Reservation',
            'check_in': '2022-04-01',
            'check_out': '2022-04-05'
        }
        # test successfull case
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        # test failure case with same data
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        data = {
            'rental_id': self.rental.id,
            'name': 'Another Test Reservation',
            'check_in': '2022-04-10',
            'check_out': '2022-04-06'
        }
        # test failure case with check_out date before check_in date
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        data = {
            'rental_id': self.rental.id,
            'name': 'Another Test Reservation',
            'check_in': '2022-04-02',
            'check_out': '2022-04-05'
        }
        # test failure case with unavailable reservation
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
