from rest_framework import serializers
from .models import Listing, Booking, Payment

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('payment_reference', 'created_at', 'updated_at', 'completed_at')

class PaymentInitiationSerializer(serializers.Serializer):
    """
    Serializer for initiating payment
    """
    booking_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='ETB')
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)

class PaymentVerificationSerializer(serializers.Serializer):
    """
    Serializer for payment verification
    """
    payment_reference = serializers.UUIDField()
