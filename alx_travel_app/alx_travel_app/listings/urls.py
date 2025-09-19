from django.urls import path
from . import views

urlpatterns = [
    # Listings endpoints
    path('listings/', views.listing_list, name='listing-list'),
    path('listings/<int:pk>/', views.listing_detail, name='listing-detail'),
    
    # Booking endpoints
    path('bookings/', views.create_booking, name='create-booking'),
    
    # Payment endpoints
    path('payments/initiate/', views.initiate_payment, name='initiate-payment'),
    path('payments/verify/', views.verify_payment, name='verify-payment'),
    path('payments/<uuid:payment_reference>/', views.payment_status, name='payment-status'),
    path('payments/user/', views.user_payments, name='user-payments'),
]

