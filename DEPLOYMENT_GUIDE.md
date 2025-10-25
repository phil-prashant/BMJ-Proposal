# 🚀 Quick Railway Deployment Guide

## Prerequisites Checklist
- ✅ GitHub account with access to `phil-prashant/BMJ-Proposal` repository
- ✅ Railway account (sign up at https://railway.app - free tier available)
- ✅ API Keys ready:
  - Resend API Key: `re_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN`
  - EmailJS Service ID: `service_kkb35zr`
  - EmailJS Template ID: `template_dbqjamx`
  - EmailJS Public Key: `lWcX2ZAuSeQUVvyNk`

---

## Step-by-Step Deployment Process

### 📝 Step 1: Access Railway
1. Go to **https://railway.app**
2. Click **"Login"** or **"Start a New Project"**
3. Sign in with your GitHub account
4. Authorize Railway to access your GitHub repositories

### 🔗 Step 2: Create New Project
1. On Railway dashboard, click **"+ New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **`phil-prashant/BMJ-Proposal`** from the list
4. Click **"Deploy Now"**

Railway will automatically:
- Detect it's a Python project
- Find `requirements.txt` and install dependencies
- Use the `Procfile` to start the application with gunicorn

### ⚙️ Step 3: Configure Environment Variables
1. Once the project is created, click on your service
2. Go to the **"Variables"** tab
3. Click **"+ New Variable"** and add these one by one:

```bash
RESEND_API_KEY=re_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN
EMAILJS_SERVICE_ID=service_kkb35zr
EMAILJS_TEMPLATE_ID=template_dbqjamx
EMAILJS_PUBLIC_KEY=lWcX2ZAuSeQUVvyNk
```

4. Click **"Add"** after each variable
5. Railway will automatically redeploy with the new variables

### 🌐 Step 4: Generate Public Domain
1. Go to the **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Railway will provide a URL like: `https://bmj-proposal-production-xxxx.up.railway.app`
5. **Copy this URL** - this is your production API endpoint

### ✅ Step 5: Verify Deployment
1. Go to the **"Deployments"** tab
2. Check that the latest deployment shows:
   - ✅ Status: **Success** (green)
   - Build completed successfully
   - Application running

3. **Test the health endpoint:**
   Open in browser or use curl:
   ```bash
   https://your-app-name.up.railway.app/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-10-25T11:00:00.000000",
     "service": "BMJ-Machinery Email Server"
   }
   ```

### 📧 Step 6: Test Email Sending
Use this curl command (replace URL with your Railway domain):

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
      "addOns": ["Analytics Dashboard"],
      "leads": "15-20",
      "meetings": "8-12",
      "traffic": "30-40%"
    }
  }'
```

---

## 🎯 Important Configuration Details

### Port Configuration
- **Application Port:** 5000 (configured in app.py)
- **Railway Port:** Automatically assigned via `$PORT` environment variable
- **Procfile command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

The app is configured to:
1. Use Railway's `$PORT` environment variable in production
2. Fallback to port 5000 for local development
3. Run with gunicorn (production-grade WSGI server)

### Environment Variables
Railway automatically sets:
- `PORT` - The port your app should listen on
- `RAILWAY_ENVIRONMENT` - Deployment environment
- `RAILWAY_PUBLIC_DOMAIN` - Your app's public URL

You need to manually set:
- `RESEND_API_KEY` - For primary email service
- `EMAILJS_SERVICE_ID` - For fallback email service
- `EMAILJS_TEMPLATE_ID` - EmailJS template
- `EMAILJS_PUBLIC_KEY` - EmailJS public key

---

## 📊 Monitoring Your Deployment

### View Logs
1. Go to your Railway project
2. Click on the service
3. Click **"Deployments"** tab
4. Select the active deployment
5. View:
   - **Build Logs** - Shows dependency installation
   - **Deploy Logs** - Shows application startup
   - **Application Logs** - Runtime logs from your Flask app

### Check Application Status
- **Health Check Endpoint:** `GET /health`
- **Expected Response Time:** < 500ms
- **Uptime Monitoring:** Railway provides built-in uptime monitoring

---

## 🔄 Automatic Redeployment

Railway automatically redeploys when you:
1. Push code changes to GitHub
2. Update environment variables
3. Manually trigger a redeploy from the dashboard

**How to trigger a manual redeploy:**
1. Go to **"Deployments"** tab
2. Click the **"..."** menu on the latest deployment
3. Select **"Redeploy"**

---

## 🐛 Troubleshooting Common Issues

### Issue: Build Fails
**Solution:**
- Check **"Build Logs"** for errors
- Verify `requirements.txt` has all dependencies
- Ensure Python version compatibility (3.9+)

### Issue: Application Crashes on Startup
**Solution:**
- Check **"Deploy Logs"** for error messages
- Verify all environment variables are set
- Check that `PORT` environment variable is being used
- Look for import errors or missing dependencies

### Issue: Health Check Fails
**Solution:**
- Verify the app is listening on `0.0.0.0:$PORT`
- Check that `/health` endpoint exists in app.py
- Review application logs for startup errors

### Issue: Emails Not Sending
**Solution:**
- Verify `RESEND_API_KEY` is correct
- Check EmailJS credentials for fallback
- Review application logs for API errors
- Test with the `/api/test-email` endpoint first

### Issue: 502 Bad Gateway
**Solution:**
- Check if app is binding to correct port (`$PORT`)
- Verify gunicorn is starting correctly
- Check memory/resource limits
- Review application startup logs

---

## 📱 Using Your Deployed API

### Base URL
```
https://your-app-name.up.railway.app
```

### Available Endpoints

#### 1. Health Check
```bash
GET /health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T11:00:00.000000",
  "service": "BMJ-Machinery Email Server"
}
```

#### 2. Send Proposal Email
```bash
POST /api/send-email
Content-Type: application/json

{
  "recipientEmail": "recipient@example.com",
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
}
```

#### 3. Test Email (Development)
```bash
POST /api/test-email
```

### Frontend Integration
Update your frontend code to use the Railway URL:

```javascript
// Before (local development)
const API_URL = 'http://localhost:5000';

// After (production)
const API_URL = 'https://your-app-name.up.railway.app';
```

---

## 💰 Railway Pricing

- **Free Tier:** $5 of usage credits per month
- **Pro Plan:** $20/month + usage
- **Usage Costs:** Based on compute time and resources
- **This app typically uses:** ~$1-3/month on free tier

---

## 📞 Support & Resources

- **Railway Documentation:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Project Support:** prashant@neoticai.com
- **GitHub Issues:** https://github.com/phil-prashant/BMJ-Proposal/issues

---

## ✅ Deployment Checklist

Use this checklist to ensure everything is configured correctly:

- [ ] Railway account created and GitHub connected
- [ ] New project created from `phil-prashant/BMJ-Proposal` repository
- [ ] All environment variables added (RESEND_API_KEY, EMAILJS credentials)
- [ ] Public domain generated
- [ ] Deployment status shows "Success" (green)
- [ ] Health check endpoint returns 200 OK
- [ ] Test email sent successfully
- [ ] Application logs show no errors
- [ ] Frontend updated with production API URL (if applicable)

---

**🎉 Once all items are checked, your Flask app is successfully deployed to Railway!**

For detailed information, refer to the main [README.md](README.md) file.
