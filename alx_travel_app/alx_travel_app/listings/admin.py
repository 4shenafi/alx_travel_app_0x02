from django.contrib import admin
from .models import Listing, Booking, Review, Payment

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price_per_night', 'owner', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'start_date', 'end_date', 'guests', 'created_at')
    list_filter = ('start_date', 'end_date', 'created_at')
    search_fields = ('user__username', 'listing__title')
    readonly_fields = ('created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'listing__title', 'comment')
    readonly_fields = ('created_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'booking', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('payment_reference', 'chapa_transaction_id', 'booking__user__username')
    readonly_fields = ('payment_reference', 'created_at', 'updated_at', 'completed_at')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_reference', 'booking', 'amount', 'currency', 'status')
        }),
        ('Chapa API Details', {
            'fields': ('chapa_transaction_id', 'chapa_checkout_url', 'payment_method')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('failure_reason',),
            'classes': ('collapse',)
        }),
    )
