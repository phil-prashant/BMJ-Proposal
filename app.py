from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this import
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import base64
import logging

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["https://bmj.neoticai.com", "http://localhost:3000"]}})  # Enable CORS for your domains
app.logger.setLevel(logging.DEBUG)

@app.route('/api/send-proposal', methods=['POST', 'OPTIONS'])  # Handle OPTIONS for preflight
def send_proposal():
    if request.method == 'OPTIONS':
        return '', 200  # Respond OK to preflight

    try:
        data = request.json
        app.logger.debug(f"Received data: {data}")

        # Validate required fields
        if not all(k in data for k in ['recipientEmail', 'selectedPackage', 'totalAmount']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Fetch env vars
        api_key = os.environ.get('SENDGRID_API_KEY')
        from_email = os.environ.get('FROM_EMAIL', 'elena@neoticai.email.com')
        cc_email = os.environ.get('CC_EMAIL', 'work@neoticai.com')

        if not api_key:
            app.logger.error("SENDGRID_API_KEY missing")
            return jsonify({'success': False, 'error': 'API key not configured'}), 500

        # Generate PDF
        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=letter)
        p.drawString(100, 750, f"Proposal for {data.get('clientName', 'Client')}")  # Use dynamic clientName
        p.drawString(100, 730, f"Package: {data['selectedPackage']}")
        p.drawString(100, 710, f"Total: ${data['totalAmount']}")
        p.drawString(100, 690, f"Email: {data['recipientEmail']}")
        if data.get('selectedAddons'):
            p.drawString(100, 670, f"Add-ons: {', '.join([addon['name'] for addon in data['selectedAddons']])}")
        p.save()
        pdf_buffer.seek(0)
        pdf_base64 = base64.b64encode(pdf_buffer.read()).decode()

        # SendGrid setup
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        from_email_obj = Email(from_email)
        to_email_obj = To(data['recipientEmail'])
        subject = "Your Custom Marketing Proposal - BMJ Machinery"
        content = Content("text/plain", f"Hi {data.get('clientName', 'Client')},\n\nAttached is your customized proposal.\n\nBest,\nBMJ Team")
        mail = Mail(from_email_obj, to_email_obj, subject, content)

        # Add CC
        if cc_email:
            mail.add_cc(cc_email)

        # Attach PDF
        attachment = Attachment(
            FileContent(pdf_base64),
            FileName('proposal.pdf'),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        mail.attachment = attachment

        response = sg.send(mail)
        app.logger.info(f"SendGrid response: {response.status_code} - {response.body}")

        if response.status_code == 202:
            return jsonify({'success': True, 'message': 'Email sent successfully'})
        else:
            app.logger.error(f"SendGrid failed: {response.status_code} - {response.body}")
            return jsonify({'success': False, 'error': f'SendGrid error: {response.status_code}'}), 500

    except Exception as e:
        app.logger.error(f"Proposal send error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
