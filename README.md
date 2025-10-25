# BMJ-Machinery Proposal Email Server

Flask-based email server for sending custom marketing proposals to BMJ-Machinery clients.

## Features

- Send proposal emails via Resend API (primary)
- EmailJS fallback for reliability
- CORS-enabled for frontend integration
- Health check endpoint
- Test email endpoint

## Deployment to Render.com

This application is configured for easy deployment to Render.com using the included `render.yaml` configuration.

### Option 1: Deploy via Render Dashboard (Recommended)

1. Push this repository to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and configure:
   - Service name: `bmj-proposal-backend`
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Environment variables:
     - `RESEND_API_KEY`
     - `EMAILJS_SERVICE_ID`

### Option 2: Deploy via Render Dashboard (Manual)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `bmj-proposal-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add Environment Variables:
   - `RESEND_API_KEY` = `re_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN`
   - `EMAILJS_SERVICE_ID` = `service_kkb35zr`
6. Click "Create Web Service"

### Environment Variables

The following environment variables are required:

- `RESEND_API_KEY`: API key for Resend email service
- `EMAILJS_SERVICE_ID`: Service ID for EmailJS fallback

Optional variables (have defaults in code):
- `EMAILJS_TEMPLATE_ID`: Template ID for EmailJS (default: `template_dbqjamx`)
- `EMAILJS_PUBLIC_KEY`: Public key for EmailJS (default: `lWcX2ZAuSeQUVvyNk`)

## Local Development

### Prerequisites

- Python 3.12+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/phil-prashant/BMJ-Proposal.git
   cd BMJ-Proposal
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Create `.env` file:
   ```env
   RESEND_API_KEY=your_resend_api_key
   EMAILJS_SERVICE_ID=your_emailjs_service_id
   ```

4. Run the development server:
   ```bash
   python app.py
   ```

   Or run with gunicorn (production-like):
   ```bash
   gunicorn app:app
   ```

5. Test the server:
   ```bash
   curl http://localhost:5000/health
   ```

## API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T11:00:00",
  "service": "BMJ-Machinery Email Server"
}
```

### `POST /api/send-email`
Send a custom proposal email.

**Request Body:**
```json
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

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully via Resend!",
  "service": "resend",
  "email_id": "abc123",
  "recipient": "client@example.com"
}
```

### `POST /api/test-email`
Send a test email to `prashant.kay3@gmail.com`.

**Response:** Same as `/api/send-email`

## Dependencies

- Flask 3.0.0 - Web framework
- flask-cors 4.0.0 - CORS support
- requests 2.31.0 - HTTP requests
- python-dotenv 1.0.0 - Environment variable management
- gunicorn 21.2.0 - Production WSGI server

## License

Proprietary - NeoticAI
