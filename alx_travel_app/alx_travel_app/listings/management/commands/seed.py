from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample listings'

    def handle(self, *args, **kwargs):
        if not User.objects.exists():
            user = User.objects.create_user(username='owner', password='password')
        else:
            user = User.objects.first()

        sample_listings = [
            {
                'title': 'Cozy Cottage',
                'description': 'A cozy cottage in the countryside.',
                'location': 'Countryside',
                'price_per_night': 120.00,
            },
            {
                'title': 'Beach House',
                'description': 'Enjoy the sea breeze in this beach house.',
                'location': 'Beachside',
                'price_per_night': 200.00,
            },
            {
                'title': 'City Apartment',
                'description': 'Modern apartment in the city center.',
                'location': 'City Center',
                'price_per_night': 150.00,
            },
        ]

        for data in sample_listings:
            Listing.objects.get_or_create(owner=user, **data)

        self.stdout.write(self.style.SUCCESS('Sample listings seeded successfully.'))
