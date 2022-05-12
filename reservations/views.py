from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from utils.custom_exception_handler import get_response

from .models import Reservation
from .serializers import ReservationSerializer

# Create your views here.


class ReservationsCreateListView(GenericAPIView):
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()

    def get(self, request):
        reservations = self.get_queryset()
        serializer = self.serializer_class(reservations, many=True)
        return Response(get_response(message="Reservations successfully fetched", result=serializer.data, success=True, status=HTTP_200_OK), status=HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(get_response(message="Reservation successfully created", result=serializer.data, success=True, status=HTTP_200_OK), status=HTTP_200_OK)
        return Response(get_response(message="Reservation creation failed", errors=serializer.errors, success=False, status=HTTP_400_BAD_REQUEST), status=HTTP_400_BAD_REQUEST)
