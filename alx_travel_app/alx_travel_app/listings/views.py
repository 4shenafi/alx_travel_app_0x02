from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
import requests
import json
from .models import Listing, Booking, Payment
from .serializers import (
    ListingSerializer, 
    BookingSerializer, 
    PaymentSerializer,
    PaymentInitiationSerializer,
    PaymentVerificationSerializer
)
from .tasks import send_payment_confirmation_email, send_payment_failure_email

# Create your views here.

@api_view(['GET'])
def listing_list(request):
    """
    List all listings
    """
    listings = Listing.objects.all()
    serializer = ListingSerializer(listings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def listing_detail(request, pk):
    """
    Retrieve a specific listing
    """
    try:
        listing = Listing.objects.get(pk=pk)
        serializer = ListingSerializer(listing)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({'error': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    """
    Create a new booking
    """
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        booking = serializer.save(user=request.user)
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    Initiate payment with Chapa API
    """
    serializer = PaymentInitiationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get booking
        booking = Booking.objects.get(
            id=serializer.validated_data['booking_id'],
            user=request.user
        )
        
        # Check if payment already exists
        if hasattr(booking, 'payment'):
            return Response(
                {'error': 'Payment already exists for this booking'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=serializer.validated_data['amount'],
            currency=serializer.validated_data['currency']
        )
        
        # Prepare Chapa API request
        chapa_data = {
            "amount": str(serializer.validated_data['amount']),
            "currency": serializer.validated_data['currency'],
            "email": serializer.validated_data['email'],
            "first_name": serializer.validated_data['first_name'],
            "last_name": serializer.validated_data['last_name'],
            "phone_number": serializer.validated_data['phone_number'],
            "tx_ref": str(payment.payment_reference),
            "callback_url": f"{request.build_absolute_uri('/')}api/payments/verify/",
            "return_url": f"{request.build_absolute_uri('/')}api/payments/success/",
            "customization": {
                "title": f"Payment for {booking.listing.title}",
                "description": f"Booking payment for {booking.listing.location}"
            }
        }
        
        # Make request to Chapa API
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{settings.CHAPA_BASE_URL}/transaction/initialize",
            headers=headers,
            data=json.dumps(chapa_data)
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Update payment with Chapa response
            payment.chapa_transaction_id = response_data.get('data', {}).get('reference')
            payment.chapa_checkout_url = response_data.get('data', {}).get('checkout_url')
            payment.save()
            
            return Response({
                'payment_reference': payment.payment_reference,
                'checkout_url': payment.chapa_checkout_url,
                'status': payment.status,
                'message': 'Payment initiated successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            # Payment initiation failed
            payment.status = 'failed'
            payment.failure_reason = response.text
            payment.save()
            
            return Response({
                'error': 'Failed to initiate payment',
                'details': response.text
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Booking.DoesNotExist:
        return Response(
            {'error': 'Booking not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def verify_payment(request):
    """
    Verify payment status with Chapa API
    """
    serializer = PaymentVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payment = Payment.objects.get(
            payment_reference=serializer.validated_data['payment_reference']
        )
        
        # Make request to Chapa API to verify payment
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{settings.CHAPA_BASE_URL}/transaction/verify/{payment.chapa_transaction_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            response_data = response.json()
            chapa_status = response_data.get('data', {}).get('status')
            
            # Update payment status based on Chapa response
            if chapa_status == 'success':
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.payment_method = response_data.get('data', {}).get('payment_method', 'Unknown')
                payment.save()
                
                # Send confirmation email
                send_payment_confirmation_email.delay(payment.id)
                
                return Response({
                    'payment_reference': payment.payment_reference,
                    'status': payment.status,
                    'message': 'Payment verified and completed successfully'
                }, status=status.HTTP_200_OK)
            else:
                payment.status = 'failed'
                payment.failure_reason = response_data.get('message', 'Payment failed')
                payment.save()
                
                # Send failure email
                send_payment_failure_email.delay(payment.id)
                
                return Response({
                    'payment_reference': payment.payment_reference,
                    'status': payment.status,
                    'message': 'Payment verification failed'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Failed to verify payment',
                'details': response.text
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, payment_reference):
    """
    Get payment status by reference
    """
    try:
        payment = Payment.objects.get(payment_reference=payment_reference)
        
        # Check if user has permission to view this payment
        if payment.booking.user != request.user:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
        
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_payments(request):
    """
    Get all payments for the authenticated user
    """
    payments = Payment.objects.filter(booking__user=request.user)
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)
