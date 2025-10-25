# Railway Deployment Configuration Summary

## 📋 Files Created for Railway Deployment

### 1. requirements.txt
**Purpose:** Lists all Python dependencies for Railway to install

**Contents:**
```
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

**Why these packages:**
- `Flask` - Web framework for the API
- `flask-cors` - Enables CORS for frontend integration
- `requests` - HTTP library for calling Resend/EmailJS APIs
- `python-dotenv` - Loads environment variables from .env file (local development)
- `gunicorn` - Production-grade WSGI HTTP server (Railway uses this)

---

### 2. Procfile
**Purpose:** Tells Railway how to start the application

**Contents:**
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

**Explanation:**
- `web:` - Defines a web process type
- `gunicorn` - Uses gunicorn instead of Flask's dev server
- `app:app` - Points to the Flask app instance in app.py
- `--bind 0.0.0.0:$PORT` - Binds to all interfaces on Railway's assigned port

---

### 3. railway.json
**Purpose:** Railway-specific configuration and deployment settings

**Contents:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Key Settings:**
- `builder: NIXPACKS` - Uses Railway's Nixpacks builder (auto-detects Python)
- `healthcheckPath: /health` - Railway pings this endpoint to verify app health
- `restartPolicyType: ON_FAILURE` - Automatically restarts if app crashes
- `restartPolicyMaxRetries: 10` - Retries up to 10 times before giving up

---

### 4. .env.example
**Purpose:** Template for environment variables (not committed to git)

**Contents:**
```bash
RESEND_API_KEY=re_your_api_key_here
EMAILJS_SERVICE_ID=service_your_service_id
EMAILJS_TEMPLATE_ID=template_your_template_id
EMAILJS_PUBLIC_KEY=your_public_key_here
PORT=5000
```

**Note:** Users copy this to `.env` for local development. On Railway, these are set through the dashboard.

---

### 5. .gitignore
**Purpose:** Prevents sensitive and generated files from being committed

**Key Exclusions:**
- `.env` - Environment variables with secrets
- `__pycache__/` - Python compiled files
- `*.pyc` - Python bytecode
- `venv/` - Virtual environment folder
- IDE and OS specific files

---

### 6. README.md
**Purpose:** Complete documentation with deployment instructions

**Sections:**
- Project overview and features
- API endpoints documentation
- Local development setup
- **Detailed Railway deployment steps (8 steps)**
- Environment variables reference
- Troubleshooting guide

---

### 7. DEPLOYMENT_GUIDE.md
**Purpose:** Quick-reference Railway deployment guide

**Sections:**
- Prerequisites checklist
- 6-step deployment process with screenshots context
- Port configuration details
- Monitoring and logging
- Automatic redeployment info
- Troubleshooting common issues
- API usage examples
- Deployment checklist

---

### 8. app.py (Modified)
**Purpose:** Updated to use Railway's PORT environment variable

**Change Made:**
```python
# Before
app.run(debug=True, host='0.0.0.0', port=5000)

# After
port = int(os.getenv('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)
```

**Why:** Railway assigns a dynamic port via `$PORT` environment variable. The app now uses this in production while defaulting to 5000 locally.

---

## 🔐 Environment Variables Configuration

### Variables to Set in Railway Dashboard

| Variable | Value | Purpose |
|----------|-------|---------|
| `RESEND_API_KEY` | `re_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN` | Primary email service API key |
| `EMAILJS_SERVICE_ID` | `service_kkb35zr` | Fallback email service ID |
| `EMAILJS_TEMPLATE_ID` | `template_dbqjamx` | EmailJS email template |
| `EMAILJS_PUBLIC_KEY` | `lWcX2ZAuSeQUVvyNk` | EmailJS authentication key |

**Note:** `PORT` is automatically set by Railway, no need to manually add it.

---

## ⚙️ Application Configuration

### Port: 5000
- **Local Development:** Explicitly set to 5000
- **Railway Production:** Uses `$PORT` environment variable (Railway assigns this)
- **Binding:** `0.0.0.0` (all network interfaces)

### Web Server
- **Local:** Flask development server (when running `python app.py`)
- **Production (Railway):** Gunicorn WSGI server
  - Better performance
  - Production-ready
  - Handles concurrent requests

### Health Check
- **Endpoint:** `GET /health`
- **Response:** JSON with status, timestamp, and service name
- **Used by:** Railway to monitor app health
- **Frequency:** Railway checks every 30 seconds

---

## 🚀 Deployment Flow

### When you deploy to Railway:

1. **Railway connects to GitHub**
   - Monitors the `phil-prashant/BMJ-Proposal` repository
   - Watches for new commits

2. **Build Phase**
   - Detects Python project from `requirements.txt`
   - Installs dependencies using pip
   - Uses Nixpacks builder

3. **Deploy Phase**
   - Runs command from `Procfile`: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Sets environment variables
   - Assigns a port number to `$PORT`

4. **Health Check**
   - Railway calls `GET /health`
   - Expects 200 OK response
   - Marks deployment as successful

5. **Public Access**
   - Generates a public domain: `https://bmj-proposal-production.up.railway.app`
   - Routes traffic to your app
   - Provides SSL certificate automatically

---

## ✅ Testing Performed

All configurations have been tested locally:

### 1. Dependencies Installation
```bash
✓ pip install -r requirements.txt
✓ All packages installed successfully
```

### 2. Flask Dev Server
```bash
✓ python app.py
✓ Server started on port 5000
✓ Health endpoint returned 200 OK
```

### 3. Gunicorn Production Server
```bash
✓ gunicorn app:app --bind 0.0.0.0:5000
✓ Server started successfully
✓ Health endpoint returned 200 OK
```

### 4. App Import Test
```bash
✓ python -c "import app"
✓ No import errors
✓ Configuration loaded correctly
```

---

## 📊 Expected Railway Deployment Logs

### Build Logs
```
Installing Python 3.12.x
Installing dependencies from requirements.txt
Collecting Flask==3.0.0
Collecting flask-cors==4.0.0
Collecting requests==2.31.0
Collecting python-dotenv==1.0.0
Collecting gunicorn==21.2.0
Successfully installed Flask-3.0.0 ...
Build completed successfully
```

### Deploy Logs
```
Starting gunicorn 21.2.0
Listening at: http://0.0.0.0:8080 (or Railway's assigned port)
Using worker: sync
Booting worker with pid: xxx

============================================================
BMJ-Machinery Proposal Email Server
============================================================
✓ Resend API Key loaded: re_73miNRj...
✓ EmailJS Service ID: service_kkb35zr
✓ CORS enabled
============================================================
```

---

## 🎯 Next Steps After Deployment

1. **Get your Railway URL** from the Settings → Domains section
2. **Test the health endpoint** in your browser
3. **Send a test email** using curl or Postman
4. **Update your frontend** (HTML files) with the production API URL
5. **Monitor logs** for any issues
6. **Set up custom domain** (optional)

---

## 📞 Support

If you encounter any issues during deployment:

1. **Check Railway Logs:**
   - Build logs for dependency issues
   - Deploy logs for startup errors
   - Application logs for runtime issues

2. **Verify Environment Variables:**
   - All 4 variables are set correctly
   - No typos in variable names
   - No extra spaces in values

3. **Common Fixes:**
   - Redeploy from Railway dashboard
   - Clear Railway cache and rebuild
   - Check Railway service status

4. **Get Help:**
   - Railway Documentation: https://docs.railway.app
   - Railway Discord: https://discord.gg/railway
   - Email: prashant@neoticai.com

---

**✅ All configuration files are ready. The application is tested and ready for Railway deployment!**
