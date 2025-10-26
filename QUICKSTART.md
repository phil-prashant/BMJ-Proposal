# Quick Start Guide

## Running the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
python app.py
```

The server will start on http://localhost:5000

### 3. Open the Frontend
Open `index.html` in your web browser.

## Configuration

All configuration is in the `.env` file:
- `SENDGRID_API_KEY` - Your SendGrid API key
- `SENDER_EMAIL` - Email address for sending
- `SENDER_NAME` - Sender name
- `FLASK_DEBUG` - Set to `True` for development, `False` for production

## Testing the Integration

1. Select a marketing package
2. Add any desired add-ons
3. Choose payment frequency
4. Click "Finalize Selections"
5. Accept the terms
6. Click "Email Proposal"
7. Enter recipient email
8. Click "Send Email with PDF"

The email will be sent via SendGrid with a PDF attachment.

## Troubleshooting

**Server won't start:**
- Check that all environment variables are set in `.env`
- Verify SendGrid API key is valid

**Email not sending:**
- Check server console for error messages
- Verify sender email is verified in SendGrid dashboard
- Check SendGrid API key permissions

**Frontend can't connect to backend:**
- Ensure backend server is running on port 5000
- Check browser console for CORS errors
