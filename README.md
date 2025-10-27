# BMJ-Machinery Proposal System

Interactive proposal builder with email delivery via SendGrid.

## Features

- 📊 Interactive proposal builder with real-time calculations
- 📧 Email delivery via SendGrid API
- 📄 Automatic PDF generation
- 💰 Package selection with add-ons
- 🎨 Professional email templates
- 📱 Responsive web interface

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/phil-prashant/BMJ-Proposal.git
cd BMJ-Proposal
```

### 2. Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=your_email@domain.com
SENDER_NAME=Your Name
CC_EMAIL=cc_recipient@domain.com
FLASK_ENV=production
```

### 4. Run the Application

Start the Flask backend server:

```bash
python app.py
```

The server will run on `http://localhost:5000`

### 5. Access the Application

Open `index.html` in your web browser or serve it through a web server.

For local development, you can use:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000`

## Deployment

### Initial Git Setup (for new repository)

If you're setting up a new repository from scratch:

```bash
git init
git add .
git commit -m "Initial commit - Complete proposal system"
git remote add origin https://github.com/your-username/your-repo-name.git
git branch -M main
git push -u origin main
```

### Production Deployment

The application can be deployed using Gunicorn:

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/send-email` - Send proposal email with PDF attachment

## Technologies Used

- **Backend**: Flask, SendGrid, ReportLab
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Email**: SendGrid API
- **PDF Generation**: ReportLab

## License

Proprietary - BMJ-Machinery Marketing Solutions
