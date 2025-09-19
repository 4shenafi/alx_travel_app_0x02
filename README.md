# ALX Travel App 0x02 - Chapa Payment Integration

This project extends the ALX Travel App with Chapa API integration for secure payment processing. Users can now make bookings with secure payment options through the Chapa payment gateway.

## Features

- **Payment Processing**: Secure payment processing using Chapa API
- **Payment Verification**: Real-time payment status verification
- **Email Notifications**: Automated email notifications for payment confirmations and failures
- **Background Tasks**: Asynchronous email sending using Celery
- **Admin Interface**: Comprehensive admin interface for managing payments
- **API Documentation**: Swagger/OpenAPI documentation

## Project Structure

```
alx_travel_app_0x02/
├── alx_travel_app/
│   ├── alx_travel_app/
│   │   ├── __init__.py
│   │   ├── celery.py          # Celery configuration
│   │   ├── settings.py        # Django settings with Chapa config
│   │   ├── urls.py           # Main URL configuration
│   │   └── wsgi.py
│   ├── listings/
│   │   ├── models.py         # Payment model and existing models
│   │   ├── views.py          # Payment API endpoints
│   │   ├── serializers.py    # Payment serializers
│   │   ├── urls.py           # Listing and payment URLs
│   │   ├── admin.py          # Admin interface for payments
│   │   └── tasks.py          # Celery tasks for email notifications
│   ├── manage.py
│   └── requirement.txt       # Updated dependencies
└── README.md
```

## Installation and Setup

### 1. Clone and Setup Environment

```bash
# Navigate to the project directory
cd alx_travel_app_0x02/alx_travel_app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirement.txt
```

### 2. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Chapa API Configuration
CHAPA_SECRET_KEY=CHASECK_TEST-your-test-secret-key
CHAPA_PUBLIC_KEY=CHAPUBK_TEST-your-test-public-key
CHAPA_BASE_URL=https://api.chapa.co/v1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravel.com

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 3. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Start Services

```bash
# Start Redis (required for Celery)
redis-server

# Start Celery worker (in a new terminal)
celery -A alx_travel_app worker --loglevel=info

# Start Django development server
python manage.py runserver
```

## API Endpoints

### Listings
- `GET /listings/` - List all listings
- `GET /listings/{id}/` - Get specific listing

### Bookings
- `POST /bookings/` - Create a new booking (requires authentication)

### Payments
- `POST /payments/initiate/` - Initiate payment with Chapa
- `POST /payments/verify/` - Verify payment status
- `GET /payments/{payment_reference}/` - Get payment status
- `GET /payments/user/` - Get user's payment history

### API Documentation
- `GET /swagger/` - Swagger UI documentation

## Payment Workflow

### 1. Create Booking
```json
POST /bookings/
{
    "listing": 1,
    "start_date": "2024-02-01",
    "end_date": "2024-02-05",
    "guests": 2
}
```

### 2. Initiate Payment
```json
POST /payments/initiate/
{
    "booking_id": 1,
    "amount": "500.00",
    "currency": "ETB",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+251911234567"
}
```

Response:
```json
{
    "payment_reference": "uuid-here",
    "checkout_url": "https://checkout.chapa.co/checkout/...",
    "status": "pending",
    "message": "Payment initiated successfully"
}
```

### 3. Verify Payment
```json
POST /payments/verify/
{
    "payment_reference": "uuid-here"
}
```

## Models

### Payment Model
- `payment_reference`: Unique UUID for the payment
- `booking`: One-to-one relationship with Booking
- `amount`: Payment amount
- `currency`: Payment currency (default: ETB)
- `status`: Payment status (pending, completed, failed, cancelled)
- `chapa_transaction_id`: Chapa's transaction reference
- `chapa_checkout_url`: Chapa checkout URL
- `payment_method`: Payment method used
- `failure_reason`: Reason for payment failure
- Timestamps: `created_at`, `updated_at`, `completed_at`

## Chapa API Integration

### Configuration
The app is configured to work with Chapa's sandbox environment for testing. Update the environment variables with your actual Chapa API keys for production.

### Supported Features
- Payment initialization
- Payment verification
- Transaction status tracking
- Webhook support (callback URLs)
- Custom payment pages

## Email Notifications

The app sends automated emails for:
- **Payment Confirmation**: When payment is successfully completed
- **Payment Failure**: When payment fails or is cancelled

Emails are sent asynchronously using Celery to avoid blocking the API response.

## Testing

### Test Payment Flow
1. Create a listing
2. Create a booking
3. Initiate payment with test data
4. Use Chapa's test payment methods
5. Verify payment status

### Test Data
Use Chapa's test credentials and test payment methods for development and testing.

## Admin Interface

Access the admin interface at `/admin/` to:
- View and manage all payments
- Monitor payment statuses
- View transaction details
- Manage listings and bookings

## Security Considerations

- API keys are stored in environment variables
- Payment data is encrypted in transit
- User authentication required for payment operations
- Payment verification prevents duplicate processing

## Production Deployment

For production deployment:
1. Update environment variables with production Chapa API keys
2. Configure proper email settings
3. Set up Redis for Celery
4. Configure proper database (PostgreSQL recommended)
5. Set `DEBUG=False`
6. Configure proper CORS settings
7. Set up SSL certificates

## Troubleshooting

### Common Issues
1. **Celery not working**: Ensure Redis is running
2. **Email not sending**: Check email configuration
3. **Payment verification failing**: Verify Chapa API keys
4. **CORS errors**: Check CORS settings in settings.py

### Logs
Check Django logs and Celery logs for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is part of the ALX Software Engineering program.

## Support

For support, please contact the development team or refer to the Chapa API documentation.

