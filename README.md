# BMJ-Machinery Proposal Email Server

Flask application for sending custom marketing proposals via email with Resend API (primary) and EmailJS (fallback).

## Features

- 📧 Email sending via Resend API with EmailJS fallback
- 🎯 Custom proposal builder with packages and add-ons
- 💰 Dynamic pricing with payment term discounts
- 🏥 Health check endpoint for monitoring
- 🔒 CORS enabled for frontend integration

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /api/send-email` - Send custom proposal email
- `POST /api/test-email` - Send test email (development)

## Local Development

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/phil-prashant/BMJ-Proposal.git
cd BMJ-Proposal
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```
RESEND_API_KEY=re_your_actual_api_key
EMAILJS_SERVICE_ID=service_your_service_id
EMAILJS_TEMPLATE_ID=template_your_template_id
EMAILJS_PUBLIC_KEY=your_public_key
```

6. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## Railway Deployment - Step-by-Step Instructions

### Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app)
- Your API keys ready (Resend, EmailJS)

### Deployment Steps

#### Step 1: Prepare Your Repository

Your repository is already configured with the necessary files:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Railway startup command
- ✅ `railway.json` - Railway configuration
- ✅ `.gitignore` - Excludes sensitive files
- ✅ `.env.example` - Environment variable template

#### Step 2: Create a New Project on Railway

1. Go to https://railway.app and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account if prompted
5. Select the **`phil-prashant/BMJ-Proposal`** repository
6. Click **"Deploy Now"**

#### Step 3: Configure Environment Variables

1. After deployment starts, click on your project
2. Go to the **"Variables"** tab
3. Click **"+ New Variable"** and add the following:

```
RESEND_API_KEY=re_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN
EMAILJS_SERVICE_ID=service_kkb35zr
EMAILJS_TEMPLATE_ID=template_dbqjamx
EMAILJS_PUBLIC_KEY=lWcX2ZAuSeQUVvyNk
PORT=5000
```

**Note:** Replace the values above with your actual API keys if different. The PORT variable is automatically set by Railway, but we include it for clarity.

4. Click **"Add"** for each variable

#### Step 4: Configure Port Settings

Railway automatically detects the PORT from your application. The Flask app is configured to run on port 5000 by default, but will use Railway's `$PORT` environment variable when deployed.

In `app.py`, the server is set to:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

When deployed with gunicorn (via Procfile), it uses:
```
gunicorn app:app --bind 0.0.0.0:$PORT
```

Railway will automatically assign and expose the correct port.

#### Step 5: Monitor Deployment

1. Go to the **"Deployments"** tab
2. Watch the build logs - you should see:
   - Installing Python dependencies
   - Build completing successfully
   - Application starting
3. Once deployed, you'll see a green **"Success"** status

#### Step 6: Get Your Application URL

1. Click on the **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. Railway will provide a URL like: `https://your-app-name.up.railway.app`
5. Copy this URL - this is your production API endpoint

#### Step 7: Test Your Deployment

1. Test the health check endpoint:
```bash
curl https://your-app-name.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T11:00:00.000000",
  "service": "BMJ-Machinery Email Server"
}
```

2. Test sending an email (replace with your Railway URL):
```bash
curl -X POST https://your-app-name.up.railway.app/api/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "recipientEmail": "your-email@example.com",
    "proposalData": {
      "packageName": "Growth Accelerator",
      "monthlyTotal": 5985,
      "firstPayment": 10645,
      "paymentTerm": "Quarterly",
      "discount": 5,
      "addOns": ["Analytics Dashboard"],
      "leads": "15-20",
      "meetings": "8-12",
      "traffic": "30-40%"
    }
  }'
```

#### Step 8: Update Your Frontend

If you have a frontend application (like the HTML files in this repo), update the API endpoint URL from:
```javascript
const API_URL = 'http://localhost:5000';
```

To your Railway URL:
```javascript
const API_URL = 'https://your-app-name.up.railway.app';
```

### Viewing Logs

To view application logs in Railway:
1. Go to your project dashboard
2. Click on the **"Deployments"** tab
3. Click on the active deployment
4. View **"Deploy Logs"** and **"Application Logs"**

### Redeploying

Railway automatically redeploys when you push to your GitHub repository:
1. Make changes to your code
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Your changes"
git push origin main
```
3. Railway will automatically detect the changes and redeploy

### Custom Domain (Optional)

To use a custom domain:
1. Go to **Settings** → **Domains**
2. Click **"Custom Domain"**
3. Enter your domain name
4. Add the CNAME record to your DNS provider as shown
5. Wait for DNS propagation (can take up to 48 hours)

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `RESEND_API_KEY` | Resend API key for primary email service | Yes |
| `EMAILJS_SERVICE_ID` | EmailJS service ID for fallback | Yes |
| `EMAILJS_TEMPLATE_ID` | EmailJS template ID for fallback | Yes |
| `EMAILJS_PUBLIC_KEY` | EmailJS public key for fallback | Yes |
| `PORT` | Server port (automatically set by Railway) | No |

## Application Details

- **Port:** 5000 (configured in app.py and Procfile)
- **Health Check:** `/health` endpoint
- **Python Version:** 3.9+
- **Web Server:** Gunicorn (production) / Flask dev server (local)

## Troubleshooting

### Deployment fails
- Check the build logs in Railway's "Deployments" tab
- Verify all environment variables are set correctly
- Ensure `requirements.txt` lists all dependencies

### Application not responding
- Check that PORT environment variable is set
- Verify the health check endpoint: `GET /health`
- Review application logs in Railway dashboard

### Emails not sending
- Verify RESEND_API_KEY is correct
- Check EmailJS credentials as fallback
- Review application logs for error messages

## Support

For issues or questions:
- Check the Railway documentation: https://docs.railway.app
- Review application logs in Railway dashboard
- Contact: prashant@neoticai.com

## License

© 2025 NeoticAI. All rights reserved.
