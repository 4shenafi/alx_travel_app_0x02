#!/usr/bin/env python3
"""
Test script for Chapa Payment Integration
This script demonstrates the payment workflow and tests the integration
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Add the Django project to the Python path
sys.path.append('/home/ashu/Desktop/ALX/alx_travel_app_0x02/alx_travel_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Payment

User = get_user_model()

def create_test_data():
    """Create test data for payment integration"""
    print("Creating test data...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Create test listing
    listing, created = Listing.objects.get_or_create(
        title='Beautiful Beach House',
        defaults={
            'description': 'A stunning beach house with ocean views',
            'location': 'Mombasa, Kenya',
            'price_per_night': 150.00,
            'owner': user
        }
    )
    if created:
        print(f"Created test listing: {listing.title}")
    else:
        print(f"Using existing test listing: {listing.title}")
    
    # Create test booking
    start_date = datetime.now().date() + timedelta(days=7)
    end_date = start_date + timedelta(days=3)
    
    booking, created = Booking.objects.get_or_create(
        listing=listing,
        user=user,
        start_date=start_date,
        end_date=end_date,
        defaults={'guests': 2}
    )
    if created:
        print(f"Created test booking: {booking.id}")
    else:
        print(f"Using existing test booking: {booking.id}")
    
    return user, listing, booking

def test_payment_creation():
    """Test payment model creation"""
    print("\n=== Testing Payment Model Creation ===")
    
    user, listing, booking = create_test_data()
    
    # Create payment
    payment = Payment.objects.create(
        booking=booking,
        amount=450.00,  # 3 nights * 150.00
        currency='ETB'
    )
    
    print(f"Created payment: {payment.payment_reference}")
    print(f"Payment status: {payment.status}")
    print(f"Payment amount: {payment.amount} {payment.currency}")
    print(f"Related booking: {payment.booking}")
    
    return payment

def test_chapa_api_simulation():
    """Simulate Chapa API integration"""
    print("\n=== Testing Chapa API Simulation ===")
    
    payment = test_payment_creation()
    
    # Simulate Chapa API response
    chapa_response = {
        "status": "success",
        "message": "Hosted Link",
        "data": {
            "checkout_url": "https://checkout.chapa.co/checkout/payment/test-checkout-url",
            "reference": f"chapa-ref-{payment.payment_reference}",
            "amount": str(payment.amount),
            "currency": payment.currency
        }
    }
    
    # Update payment with simulated Chapa response
    payment.chapa_transaction_id = chapa_response['data']['reference']
    payment.chapa_checkout_url = chapa_response['data']['checkout_url']
    payment.save()
    
    print(f"Updated payment with Chapa transaction ID: {payment.chapa_transaction_id}")
    print(f"Checkout URL: {payment.chapa_checkout_url}")
    
    return payment

def test_payment_verification():
    """Test payment verification simulation"""
    print("\n=== Testing Payment Verification ===")
    
    payment = test_chapa_api_simulation()
    
    # Simulate successful payment verification
    verification_response = {
        "status": "success",
        "message": "Payment verified",
        "data": {
            "status": "success",
            "reference": payment.chapa_transaction_id,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "payment_method": "CARD"
        }
    }
    
    # Update payment status
    if verification_response['data']['status'] == 'success':
        payment.status = 'completed'
        payment.completed_at = datetime.now()
        payment.payment_method = verification_response['data']['payment_method']
        payment.save()
        
        print(f"Payment verified and completed!")
        print(f"Final status: {payment.status}")
        print(f"Payment method: {payment.payment_method}")
        print(f"Completed at: {payment.completed_at}")
    
    return payment

def test_payment_failure():
    """Test payment failure scenario"""
    print("\n=== Testing Payment Failure Scenario ===")
    
    user, listing, booking = create_test_data()
    
    # Create a new payment for failure test
    payment = Payment.objects.create(
        booking=booking,
        amount=300.00,
        currency='ETB'
    )
    
    # Simulate failed payment
    payment.status = 'failed'
    payment.failure_reason = 'Insufficient funds'
    payment.save()
    
    print(f"Payment failed: {payment.payment_reference}")
    print(f"Failure reason: {payment.failure_reason}")
    print(f"Status: {payment.status}")
    
    return payment

def display_payment_summary():
    """Display summary of all payments"""
    print("\n=== Payment Summary ===")
    
    payments = Payment.objects.all().order_by('-created_at')
    
    if not payments:
        print("No payments found.")
        return
    
    print(f"Total payments: {payments.count()}")
    print("\nPayment Details:")
    print("-" * 80)
    
    for payment in payments:
        print(f"Reference: {payment.payment_reference}")
        print(f"Booking: {payment.booking.listing.title}")
        print(f"User: {payment.booking.user.username}")
        print(f"Amount: {payment.amount} {payment.currency}")
        print(f"Status: {payment.status}")
        print(f"Created: {payment.created_at}")
        if payment.completed_at:
            print(f"Completed: {payment.completed_at}")
        if payment.failure_reason:
            print(f"Failure Reason: {payment.failure_reason}")
        print("-" * 80)

def main():
    """Main test function"""
    print("ALX Travel App - Chapa Payment Integration Test")
    print("=" * 50)
    
    try:
        # Test payment creation
        test_payment_creation()
        
        # Test Chapa API simulation
        test_chapa_api_simulation()
        
        # Test payment verification
        test_payment_verification()
        
        # Test payment failure
        test_payment_failure()
        
        # Display summary
        display_payment_summary()
        
        print("\n✅ All tests completed successfully!")
        print("\nTo test the actual API endpoints:")
        print("1. Start the Django server: python manage.py runserver")
        print("2. Access Swagger UI: http://localhost:8000/swagger/")
        print("3. Use the API endpoints to test payment flow")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

