# BMJ-Machinery Marketing Proposal

An interactive web-based proposal builder for BMJ-Machinery with email delivery via SendGrid.

## Features

- **Interactive Package Selection**: Choose from three marketing packages (Lead Generator, Growth Accelerator, Market Domination)
- **Customizable Add-ons**: Enhance packages with additional services
- **Flexible Payment Terms**: Monthly, Quarterly, Semi-Annual, or Annual billing with discounts
- **PDF Generation**: Automatically generates proposal PDFs
- **Email Delivery**: Send proposals via SendGrid with PDF attachments

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- SendGrid API Key (provided in environment variables)

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   The `.env` file contains the necessary SendGrid configuration:
   - `SENDGRID_API_KEY`: Your SendGrid API key
   - `SENDER_EMAIL`: Email address for sending proposals
   - `SENDER_NAME`: Name that appears as the sender
   - `FLASK_DEBUG`: Set to `True` for development, `False` for production (default: False)

3. **Start the backend server**:
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:5000`

4. **Open the frontend**:
   Open `index.html` in a web browser. The page will automatically connect to the backend.

## Usage

1. **Select a Base Package**: Choose from three marketing packages
2. **Add Customizations**: Select add-ons to enhance your package
3. **Choose Payment Terms**: Select billing frequency (discounts available for longer terms)
4. **Finalize Selection**: Lock in your choices
5. **Accept Terms**: Review and agree to the terms and conditions
6. **Send Proposal**: Enter recipient email and send the proposal with PDF

## API Endpoints

### POST /api/send-email
Sends a proposal email with PDF attachment via SendGrid.

**Request Body**:
```json
{
  "recipientEmail": "recipient@example.com",
  "proposalData": {
    "packageName": "Growth Accelerator",
    "monthlyTotal": "5500",
    "paymentTerm": "quarterly",
    "firstPayment": "15675",
    "prospects": "15-20"
  },
  "pdfBase64": "base64_encoded_pdf_data"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Email sent successfully",
  "status_code": 202
}
```

### GET /api/health
Health check endpoint to verify the service is running.

**Response**:
```json
{
  "status": "healthy",
  "service": "BMJ Proposal Email Service"
}
```

## File Structure

```
.
├── index.html              # Main proposal builder interface
├── app.py                  # Flask backend for email sending
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (DO NOT COMMIT)
├── .gitignore             # Git ignore rules
├── script.py              # Debugging notes
└── README.md              # This file
```

## Security Notes

- The `.env` file contains sensitive API keys and should never be committed to version control
- The `.gitignore` file is configured to exclude `.env` and other sensitive files
- API keys should be rotated regularly for security

## Troubleshooting

**Backend not connecting**:
- Ensure the Flask server is running on port 5000
- Check that `.env` file exists with valid credentials
- Verify CORS is enabled for your frontend domain

**Email not sending**:
- Verify SendGrid API key is valid
- Check sender email is verified in SendGrid
- Review Flask console for error messages

**PDF not generating**:
- Ensure jsPDF library is loaded correctly
- Check browser console for JavaScript errors

## Support

For issues or questions, contact: prashant@neoticai.com
