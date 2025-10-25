# Railway Deployment - Quick Reference Card

## 🚀 What Was Done

This repository is now fully configured for deployment to Railway with GitHub integration.

## 📁 Files Added

1. **requirements.txt** - Python dependencies (Flask, Flask-CORS, Requests, python-dotenv, Gunicorn)
2. **Procfile** - Railway start command: `web: gunicorn app:app --bind 0.0.0.0:$PORT`
3. **runtime.txt** - Python version: 3.12.3
4. **.env.example** - Template for environment variables (DO NOT commit .env)
5. **.gitignore** - Excludes sensitive files, cache, and virtual environments
6. **README.md** - Project overview, API documentation, quick start guide
7. **DEPLOYMENT.md** - Complete step-by-step Railway deployment instructions

## 🔧 Files Modified

- **app.py** - Updated to use Railway's `PORT` environment variable: `port = int(os.getenv('PORT', 5000))`

## 🔑 Environment Variables Required

Set these in Railway's dashboard under "Variables" tab:

| Variable | Example Value | Description |
|----------|---------------|-------------|
| `RESEND_API_KEY` | `re_xxxxx...` | Resend API key |
| `EMAILJS_SERVICE_ID` | `service_xxxxx` | EmailJS service ID |
| `EMAILJS_TEMPLATE_ID` | `template_xxxxx` | EmailJS template ID |
| `EMAILJS_PUBLIC_KEY` | `xxxxxxxxx` | EmailJS public key |
| `PORT` | `5000` | Application port (Railway auto-provides this) |
| `FLASK_ENV` | `production` | Flask environment |

## 📖 Deployment Instructions Summary

1. **Sign in to Railway**: https://railway.app
2. **Create New Project** → **Deploy from GitHub repo**
3. **Select Repository**: `phil-prashant/BMJ-Proposal`
4. **Add Environment Variables** (see table above)
5. **Generate Domain** in Settings → Domains
6. **Access Your App**: `https://your-app-name.up.railway.app`

## ✅ Health Check

Once deployed, test your app:
```bash
curl https://your-app-name.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "service": "BMJ-Machinery Email Server"
}
```

## 📋 API Endpoints

- `GET /health` - Health check
- `POST /api/send-email` - Send proposal email
- `POST /api/test-email` - Send test email

## 📚 Full Documentation

- **Detailed Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Project README**: See [README.md](README.md)

## 🔄 Continuous Deployment

Railway automatically redeploys when you push to the main branch. No manual intervention needed!

## 💡 Key Configuration Points

- **Port**: Application uses `os.getenv('PORT', 5000)` to work with Railway's dynamic port assignment
- **Server**: Uses Gunicorn (production-grade WSGI server) instead of Flask's dev server
- **CORS**: Enabled for frontend integration
- **Fallback**: Email service has Resend (primary) + EmailJS (fallback) for reliability

## ⚠️ Important Security Notes

- Never commit `.env` file (it's in `.gitignore`)
- Keep API keys in Railway's environment variables, not in code
- Use `.env.example` as a template only

## 🎯 Next Steps

1. Review [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions
2. Gather your API keys (Resend, EmailJS)
3. Follow the deployment guide
4. Test your deployed application
5. (Optional) Set up custom domain

---

**Status**: ✅ Ready for Deployment
**Port**: 5000 (configurable via Railway)
**Environment**: Production-ready
