# Deploying Flask App to Railway

This guide provides step-by-step instructions for deploying the BMJ-Proposal Flask application to Railway using GitHub integration.

## Prerequisites

- A GitHub account with access to this repository
- A Railway account (sign up at https://railway.app)
- The following API keys ready:
  - Resend API Key
  - EmailJS Service ID, Template ID, and Public Key (for fallback)

## Deployment Files Overview

This repository includes the following files required for Railway deployment:

- **`requirements.txt`**: Lists all Python dependencies needed by the Flask app
- **`Procfile`**: Tells Railway how to run the application using Gunicorn
- **`runtime.txt`**: Specifies the Python version (3.12.3)
- **`.env.example`**: Template for environment variables (DO NOT commit actual `.env` file)
- **`app.py`**: Main Flask application (configured to use Railway's PORT environment variable)

## Step-by-Step Deployment Instructions

### 1. Prepare Your Railway Account

1. Go to https://railway.app
2. Click **"Start a New Project"** or **"Login"** if you already have an account
3. Sign in with your GitHub account (recommended for seamless integration)

### 2. Create a New Project from GitHub

1. Once logged into Railway, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. If this is your first time, Railway will ask for permission to access your GitHub repositories:
   - Click **"Configure GitHub App"**
   - Select the repositories you want to give Railway access to (select this `BMJ-Proposal` repository)
   - Click **"Install & Authorize"**
4. Back in Railway, find and select the **`phil-prashant/BMJ-Proposal`** repository
5. Railway will automatically detect that this is a Python application

### 3. Configure Environment Variables

After Railway creates your project:

1. In the Railway dashboard, click on your newly created service
2. Navigate to the **"Variables"** tab
3. Add the following environment variables one by one:

   **Required Variables:**
   
   | Variable Name | Value | Description |
   |--------------|-------|-------------|
   | `RESEND_API_KEY` | `your_resend_api_key_here` | Your Resend API key for email sending |
   | `EMAILJS_SERVICE_ID` | `your_service_id` | EmailJS service ID (fallback) |
   | `EMAILJS_TEMPLATE_ID` | `your_template_id` | EmailJS template ID (fallback) |
   | `EMAILJS_PUBLIC_KEY` | `your_public_key` | EmailJS public key (fallback) |
   | `PORT` | `5000` | Application port (Railway will override this) |
   | `FLASK_ENV` | `production` | Flask environment setting |

   > **Note:** Railway automatically provides a `PORT` environment variable, but you can set a default of 5000 for consistency.

4. Click **"Add"** or **"Save"** for each variable

### 4. Configure Service Settings

1. In the Railway dashboard, go to the **"Settings"** tab of your service
2. Verify the following settings:
   - **Start Command**: Should automatically use the `Procfile` (web: gunicorn app:app --bind 0.0.0.0:$PORT)
   - **Root Directory**: Should be `/` (default)
   - **Build Command**: Should be empty (Railway will install from requirements.txt)

### 5. Deploy the Application

Railway will automatically deploy your application when:

1. You push changes to the connected GitHub repository (main/master branch by default)
2. You manually trigger a deployment from the Railway dashboard

**To manually deploy:**
1. In the Railway dashboard, go to the **"Deployments"** tab
2. Click **"Deploy"** or wait for the automatic deployment to complete
3. Monitor the build logs to ensure everything installs correctly

### 6. Access Your Deployed Application

Once deployment is complete:

1. In the Railway dashboard, go to the **"Settings"** tab
2. Scroll down to **"Domains"**
3. Click **"Generate Domain"** to get a public URL for your application
4. Railway will provide a URL like: `https://your-app-name.up.railway.app`

**Your Flask app will be available at:**
- Main URL: `https://your-app-name.up.railway.app`
- Health Check: `https://your-app-name.up.railway.app/health`
- Send Email Endpoint: `https://your-app-name.up.railway.app/api/send-email`

### 7. Test Your Deployment

1. **Test the Health Check Endpoint:**
   ```bash
   curl https://your-app-name.up.railway.app/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-10-25T10:46:15.926Z",
     "service": "BMJ-Machinery Email Server"
   }
   ```

2. **Test Email Sending (Optional):**
   ```bash
   curl -X POST https://your-app-name.up.railway.app/api/send-email \
     -H "Content-Type: application/json" \
     -d '{
       "recipientEmail": "test@example.com",
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
     }'
   ```

### 8. Set Up Automatic Deployments from GitHub

Railway automatically sets up continuous deployment from GitHub. Whenever you push to the main branch:

1. Railway detects the change
2. Rebuilds the Docker container
3. Deploys the new version automatically

**To configure which branch triggers deployments:**
1. Go to **"Settings"** tab in Railway dashboard
2. Find **"Branch"** setting
3. Select your preferred branch (default: main or master)

### 9. Monitor Your Application

Railway provides several monitoring tools:

1. **Logs**: Click "Logs" tab to view real-time application logs
2. **Metrics**: View CPU, memory, and network usage
3. **Deployments**: See deployment history and status

### 10. Custom Domain (Optional)

To use a custom domain:

1. In Railway dashboard, go to **"Settings"** → **"Domains"**
2. Click **"Add Custom Domain"**
3. Enter your domain name
4. Follow the DNS configuration instructions provided by Railway
5. Add the required CNAME record to your domain's DNS settings

## Environment Variables Reference

Based on the current `app.py` configuration:

| Variable | Required | Default Value | Description |
|----------|----------|---------------|-------------|
| `RESEND_API_KEY` | Yes | `re_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN` | Primary email service API key |
| `EMAILJS_SERVICE_ID` | Yes | `service_kkb35zr` | Fallback email service ID |
| `EMAILJS_TEMPLATE_ID` | Yes | `template_dbqjamx` | Fallback email template |
| `EMAILJS_PUBLIC_KEY` | Yes | `lWcX2ZAuSeQUVvyNk` | Fallback email public key |
| `PORT` | No | `5000` | Server port (Railway provides this) |
| `FLASK_ENV` | No | `production` | Flask environment |

> **Security Note:** Never commit your `.env` file or expose your API keys publicly. The values shown above are examples from the code and should be replaced with your actual keys in Railway's environment variables.

## Port Configuration

- **Default Port**: 5000
- **Railway Port**: Automatically assigned by Railway via `$PORT` environment variable
- **Application Configuration**: `app.py` now reads from `os.getenv('PORT', 5000)` to support both local and Railway environments

## Troubleshooting

### Build Fails

- Check that all dependencies in `requirements.txt` are valid
- Review build logs in Railway dashboard
- Ensure Python version in `runtime.txt` is supported by Railway

### Application Won't Start

- Verify the `Procfile` is present and correctly configured
- Check that environment variables are set correctly
- Review application logs in Railway dashboard

### Email Sending Fails

- Verify all email-related environment variables are set
- Check API keys are valid and active
- Review application logs for specific error messages

### Port Binding Issues

- Ensure `app.py` uses `os.getenv('PORT', 5000)` for port configuration
- Verify `Procfile` binds to `0.0.0.0:$PORT`

## API Endpoints

Once deployed, your application exposes the following endpoints:

- **GET** `/health` - Health check endpoint
- **POST** `/api/send-email` - Send proposal email
- **POST** `/api/test-email` - Send test email

## Additional Resources

- Railway Documentation: https://docs.railway.app
- Flask Deployment Guide: https://flask.palletsprojects.com/en/3.0.x/deploying/
- Gunicorn Documentation: https://docs.gunicorn.org

## Support

For issues related to:
- **Railway Platform**: https://railway.app/help
- **This Application**: Create an issue in the GitHub repository

---

**Last Updated**: 2025-10-25
