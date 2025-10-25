# Render.com Deployment Instructions

This guide will help you deploy the BMJ Proposal Flask application to Render.com.

## Prerequisites

- A Render.com account (sign up at https://render.com)
- This repository pushed to GitHub

## Deployment Steps

### 1. Create a New Web Service

1. Log in to your Render.com dashboard
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository: `phil-prashant/BMJ-Proposal`
4. Select the branch: `main` (or your preferred branch)

### 2. Configure the Service

Use the following settings:

- **Name**: `bmj-proposal-backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 3. Set Environment Variables

In the "Environment" section, add the following environment variables:

| Key | Value |
|-----|-------|
| `RESEND_API_KEY` | `re_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN` |
| `EMAILJS_SERVICE_ID` | `service_kkb35zr` |
| `PYTHON_VERSION` | `3.12.3` |

**Note**: The `RESEND_API_KEY` and `EMAILJS_SERVICE_ID` values are provided in the problem statement. Make sure to keep these secure.

### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Once deployed, you'll get a URL like: `https://bmj-proposal-backend.onrender.com`

### 5. Verify Deployment

Test your deployment by visiting:
- Health check: `https://your-service-url.onrender.com/health`
- Should return: `{"status": "healthy", "timestamp": "...", "service": "BMJ-Machinery Email Server"}`

## Using render.yaml (Alternative Method)

This repository includes a `render.yaml` file that can be used for automated deployment:

1. In Render dashboard, go to "Blueprint" → "New Blueprint Instance"
2. Connect your repository
3. Render will automatically detect the `render.yaml` file
4. You'll still need to manually set the `RESEND_API_KEY` and `EMAILJS_SERVICE_ID` values in the environment variables section

## API Endpoints

Once deployed, your application will have the following endpoints:

- `GET /health` - Health check endpoint
- `POST /api/send-email` - Send proposal email
- `POST /api/test-email` - Send test email

## Troubleshooting

- **Build fails**: Check that `requirements.txt` is in the root directory
- **App doesn't start**: Verify the start command is correct and gunicorn is installed
- **Health check fails**: Ensure the `/health` endpoint is accessible
- **Email sending fails**: Verify environment variables are set correctly

## Support

For issues with deployment, contact the development team or check Render.com documentation at https://render.com/docs
