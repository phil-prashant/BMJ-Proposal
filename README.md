# BMJ-Machinery Proposal Email Server

A Flask-based email server for sending custom marketing proposals to BMJ-Machinery clients. This application integrates with Resend (primary) and EmailJS (fallback) for reliable email delivery.

## Features

- 📧 **Dual Email Service**: Uses Resend as primary email service with EmailJS as automatic fallback
- 🎯 **Proposal Generation**: Custom HTML email templates with proposal details
- 🔒 **CORS Enabled**: Ready for frontend integration
- 💊 **Health Check**: Built-in health monitoring endpoint
- 🚀 **Production Ready**: Configured for deployment on Railway

## Quick Start (Local Development)

### Prerequisites

- Python 3.12.3 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/phil-prashant/BMJ-Proposal.git
   cd BMJ-Proposal
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your API keys:
   ```
   RESEND_API_KEY=your_actual_resend_key
   EMAILJS_SERVICE_ID=your_actual_service_id
   EMAILJS_TEMPLATE_ID=your_actual_template_id
   EMAILJS_PUBLIC_KEY=your_actual_public_key
   ```

5. Run the application:
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T10:46:15.926Z",
  "service": "BMJ-Machinery Email Server"
}
```

### Send Proposal Email
```bash
POST /api/send-email
Content-Type: application/json

{
  "recipientEmail": "client@example.com",
  "proposalData": {
    "packageName": "Growth Accelerator",
    "monthlyTotal": 5985,
    "firstPayment": 10645,
    "paymentTerm": "Quarterly",
    "discount": 5,
    "addOns": ["Analytics", "Copywriter"],
    "leads": "15-20",
    "meetings": "8-12",
    "traffic": "30-40%"
  }
}
```

### Test Email
```bash
POST /api/test-email
```

Sends a test email to the configured test address.

## Deployment to Railway

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

### Quick Deploy Steps:

1. Push this repository to GitHub
2. Sign in to [Railway](https://railway.app)
3. Create a new project from GitHub repo
4. Add environment variables (see [DEPLOYMENT.md](DEPLOYMENT.md))
5. Railway will automatically deploy using the `Procfile`

**Port Configuration**: The app automatically uses Railway's `PORT` environment variable (defaults to 5000 for local development).

## Project Structure

```
BMJ-Proposal/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Procfile                    # Railway deployment configuration
├── runtime.txt                 # Python version specification
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── DEPLOYMENT.md              # Detailed deployment guide
├── README.md                  # This file
├── index.html                 # Frontend proposal builder
├── bmj_proposal_resend.html   # Alternative frontend
└── script.py                  # HTML generation script
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RESEND_API_KEY` | Yes | Resend API key for email sending |
| `EMAILJS_SERVICE_ID` | Yes | EmailJS service ID (fallback) |
| `EMAILJS_TEMPLATE_ID` | Yes | EmailJS template ID (fallback) |
| `EMAILJS_PUBLIC_KEY` | Yes | EmailJS public key (fallback) |
| `PORT` | No | Server port (default: 5000, auto-set by Railway) |
| `FLASK_ENV` | No | Flask environment (development/production) |

## Technologies Used

- **Flask 3.0.0**: Web framework
- **Flask-CORS 4.0.0**: Cross-origin resource sharing
- **Requests 2.31.0**: HTTP library
- **python-dotenv 1.0.0**: Environment variable management
- **Gunicorn 21.2.0**: Production WSGI server

## Development

### Run with Gunicorn (Production Mode)
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

### Run with Flask Dev Server
```bash
python app.py
```

## Support

For issues or questions:
- Create an issue in the GitHub repository
- Contact: prashant@neoticai.com

## License

© 2025 NeoticAI. All rights reserved.
