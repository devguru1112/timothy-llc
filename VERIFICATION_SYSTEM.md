# Verification System Documentation

## Overview

The system now implements a comprehensive verification flow:

1. **Public Access**: Users can view and apply to jobs without registration
2. **Application Limits**: After 3 free applications (configurable), users must register
3. **Phone Verification**: Required during registration (SMS code)
4. **Email Verification**: Required after registration (email code)
5. **Full Access**: Only fully verified users (phone + email) can see all job opportunities

## Backend Changes

### User Model Updates

Added verification fields:
- `phone_verified` - Boolean
- `email_verified` - Boolean
- `phone_verification_code` - 6-digit code
- `phone_verification_code_expires` - Expiration time (10 minutes)
- `email_verification_code` - 6-digit code
- `email_verification_code_expires` - Expiration time (24 hours)

### New Services

1. **SMS Service** (`users/services.py`)
   - Supports Twilio and AWS SNS
   - Falls back to logging in development
   - Configurable via environment variables

2. **Email Verification Service** (`users/services.py`)
   - Uses existing email service infrastructure
   - Sends verification codes via email

### New Endpoints

- `POST /api/auth/verify/phone/send/` - Send phone verification code
- `POST /api/auth/verify/phone/` - Verify phone with code
- `POST /api/auth/verify/email/send/` - Send email verification code
- `POST /api/auth/verify/email/` - Verify email with code

### Application Limit Middleware

- Tracks applications per email/IP address
- Uses Django cache (24-hour TTL)
- Returns error when limit exceeded
- Configurable via `free_applications_limit` setting

### Project Access Control

- **Non-authenticated**: Limited projects (free_projects_limit)
- **Authenticated but unverified**: Limited projects (free_projects_limit)
- **Fully verified**: All projects

## Frontend Changes

### New Pages

1. **Verification Page** (`/verify`)
   - Shows phone and email verification status
   - Allows sending and verifying codes
   - Redirects to dashboard when fully verified

### Updated Pages

1. **Signup Page**
   - Phone field now required
   - Redirects to verification page after registration
   - Shows verification requirement message

2. **Public Project Detail**
   - Shows application limit warnings
   - Prompts registration when limit reached
   - Displays remaining applications

## Configuration

### Environment Variables

Add to `.env`:

```bash
# SMS Configuration (choose one)
SMS_PROVIDER=twilio  # or aws_sns

# For Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# For AWS SNS (alternative)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

### System Settings

Configure via Django Admin or API:

- `free_applications_limit`: Number of free applications (default: 3)
- `free_projects_limit`: Number of free projects shown (default: 10)

## User Flow

### 1. Public User (No Registration)

1. Visit `/public` - See limited projects
2. Apply to projects (up to limit)
3. After limit: Prompted to register

### 2. Registration Flow

1. Fill registration form (phone required)
2. Submit → Phone verification code sent via SMS
3. Redirected to `/verify` page
4. Enter phone code → Phone verified
5. Email verification code sent automatically
6. Enter email code → Email verified
7. Full access granted

### 3. Verified User

- Can see all projects
- Unlimited applications
- Full dashboard access

## Testing

### Development Mode

In `DEBUG=True` mode:
- SMS codes are logged to console/logs
- Email codes are shown in API response (for testing)

### Test Phone Verification

```python
python manage.py shell

from users.models import User
user = User.objects.get(email='test@example.com')
code = user.send_phone_verification_code()
print(f"Code: {code}")  # Check logs or console
user.verify_phone_code(code)
```

### Test Email Verification

```python
python manage.py shell

from users.models import User
user = User.objects.get(email='test@example.com')
code = user.send_email_verification_code()
print(f"Code: {code}")  # Check email or logs
user.verify_email_code(code)
```

## Migration Required

Run migrations to add new fields:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Setup Initial Settings

```bash
python manage.py shell
>>> from scripts.setup_initial_settings import setup_settings
>>> setup_settings()
```

This creates:
- `free_projects_limit` = 10
- `free_applications_limit` = 3

## API Examples

### Register User

```bash
POST /api/auth/register/
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "password2": "securepass123",
  "phone": "+1234567890"
}
```

Response includes verification requirement.

### Send Phone Verification

```bash
POST /api/auth/verify/phone/send/
Authorization: Bearer <token>
```

### Verify Phone

```bash
POST /api/auth/verify/phone/
Authorization: Bearer <token>
{
  "code": "123456"
}
```

### Send Email Verification

```bash
POST /api/auth/verify/email/send/
Authorization: Bearer <token>
```

### Verify Email

```bash
POST /api/auth/verify/email/
Authorization: Bearer <token>
{
  "code": "654321"
}
```

## Troubleshooting

### SMS Not Sending

1. Check SMS provider credentials in `.env`
2. Check logs for error messages
3. In development, codes are logged (check console)
4. Verify phone number format (E.164 format recommended)

### Email Not Sending

1. Check email service configuration
2. Verify SMTP/SendGrid/AWS SES settings
3. Check spam folder
4. In development, codes may be in logs

### Application Limit Not Working

1. Ensure cache is configured
2. Check middleware is in `MIDDLEWARE` list
3. Verify `free_applications_limit` setting exists
4. Check cache backend is running (Redis for production)

### Verification Codes Expired

- Phone codes expire in 10 minutes
- Email codes expire in 24 hours
- User can request new codes

## Security Notes

1. Codes are 6-digit random numbers
2. Codes expire after set time
3. Rate limiting should be added for production
4. Phone numbers should be validated
5. Consider adding CAPTCHA for registration
