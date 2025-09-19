from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Payment, Booking


@shared_task
def send_payment_confirmation_email(payment_id):
    """
    Send payment confirmation email to user
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        booking = payment.booking
        user = booking.user
        listing = booking.listing
        
        subject = f'Payment Confirmation - Booking for {listing.title}'
        message = f"""
        Dear {user.username},
        
        Your payment has been successfully processed!
        
        Booking Details:
        - Property: {listing.title}
        - Location: {listing.location}
        - Check-in: {booking.start_date}
        - Check-out: {booking.end_date}
        - Guests: {booking.guests}
        - Amount Paid: {payment.amount} {payment.currency}
        - Payment Reference: {payment.payment_reference}
        - Transaction ID: {payment.chapa_transaction_id}
        
        Thank you for choosing ALX Travel!
        
        Best regards,
        ALX Travel Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Payment confirmation email sent to {user.email}"
        
    except Payment.DoesNotExist:
        return f"Payment with ID {payment_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@shared_task
def send_payment_failure_email(payment_id):
    """
    Send payment failure notification email to user
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        booking = payment.booking
        user = booking.user
        listing = booking.listing
        
        subject = f'Payment Failed - Booking for {listing.title}'
        message = f"""
        Dear {user.username},
        
        Unfortunately, your payment could not be processed.
        
        Booking Details:
        - Property: {listing.title}
        - Location: {listing.location}
        - Check-in: {booking.start_date}
        - Check-out: {booking.end_date}
        - Guests: {booking.guests}
        - Amount: {payment.amount} {payment.currency}
        - Payment Reference: {payment.payment_reference}
        - Failure Reason: {payment.failure_reason or 'Unknown'}
        
        Please try again or contact our support team for assistance.
        
        Best regards,
        ALX Travel Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Payment failure email sent to {user.email}"
        
    except Payment.DoesNotExist:
        return f"Payment with ID {payment_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"
