from django.db.models import OuterRef, Subquery, Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from utils.custom_exception_handler import get_response

from .models import Rental, Reservation
from .serializers import ReservationSerializer

# Create your views here.


class ReservationsCreateListView(GenericAPIView):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        previous = Reservation.objects.filter(Q(rental=OuterRef("rental")),
                                              ~Q(id=OuterRef("pk")), Q(check_in__lt=OuterRef("check_in")))
        return Reservation.objects.annotate(previous=Subquery(previous.values('name')[:1]))

    def get(self, request):
        reservations = self.get_queryset()
        serializer = self.serializer_class(reservations, many=True)
        return Response(get_response(message="Reservations successfully fetched", result=serializer.data, success=True, status=HTTP_200_OK), status=HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(get_response(message="Reservation successfully created", result=serializer.data, success=True, status=HTTP_201_CREATED), status=HTTP_201_CREATED)
        return Response(get_response(message="Reservation creation failed", errors=serializer.errors, success=False, status=HTTP_400_BAD_REQUEST), status=HTTP_400_BAD_REQUEST)
