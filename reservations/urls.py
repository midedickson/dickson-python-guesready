from django.urls import path
from .views import ReservationsCreateListView
urlpatterns = [
    path('', ReservationsCreateListView.as_view(),
         name='reservations'),
]
