from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import base64
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)  # Enable detailed logs in Railway

# Enable CORS: Allow requests from your frontend domain (add more if needed, e.g., localhost for dev)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://bmj.neoticai.com", "http://localhost:3000"],  # Replace with your exact frontend URL(s)
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/send-proposal', methods=['POST', 'OPTIONS'])
def send_proposal():
    if request.method == 'OPTIONS':
        # Preflight handled by flask-cors, but explicit for safety
        return '', 200

    try:
        data = request.get_json()
        app.logger.debug(f"Received proposal data from {request.origin}: {data}")

        # Validate input
        required_fields = ['recipientEmail', 'selectedPackage', 'totalAmount', 'clientName', 'company']
        if not all(field in data for field in required_fields):
            app.logger.warning("Missing required fields in request")
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Fetch env vars (add these in Railway Variables if not set)
        api_key = os.environ.get('SENDGRID_API_KEY')
        from_email_str = os.environ.get('FROM_EMAIL', 'elena@neoticai.email.com')
        cc_email_str = os.environ.get('CC_EMAIL', 'work@neoticai.com')

        if not api_key:
            app.logger.error("SENDGRID_API_KEY not found in environment")
            return jsonify({'success': False, 'error': 'Server configuration error: API key missing'}), 500

        # Generate PDF proposal
        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=letter)
        y_position = 750
        p.drawString(100, y_position, f"Custom Marketing Proposal")
        y_position -= 30
        p.drawString(100, y_position, f"Client: {data['clientName']}")
        y_position -= 30
        p.drawString(100, y_position, f"Company: {data['company']}")
        y_position -= 30
        p.drawString(100, y_position, f"Selected Package: {data.get('packageDetails', {}).get('name', data['selectedPackage'])}")
        y_position -= 30
        p.drawString(100, y_position, f"Add-ons: {', '.join([addon['name'] for addon in data.get('selectedAddons', [])]) or 'None'}")
        y_position -= 30
        p.drawString(100, y_position, f"Payment: {data.get('selectedPayment', 'Monthly')}")
        y_position -= 30
        p.drawString(100, y_position, f"Total Amount: ${data['totalAmount']:,}")
        y_position -= 30
        p.drawString(100, y_position, f"Email: {data['recipientEmail']}")
        p.drawString(100, y_position - 30, "Thank you for choosing BMJ-Machinery Marketing Solutions!")
        p.save()
        pdf_buffer.seek(0)
        pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')

        # SendGrid email setup
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        from_email = Email(from_email_str)
        to_email = To(data['recipientEmail'])
        subject = f"Your Custom Marketing Proposal - {data['company']}"
        plain_text_content = f"""
Hi {data['clientName']},

Thank you for using our interactive proposal tool. Attached is your customized marketing package PDF with all selections.

Package Details:
- Base: {data.get('packageDetails', {}).get('name', data['selectedPackage'])}
- Add-ons: {', '.join([addon['name'] for addon in data.get('selectedAddons', [])]) or 'None'}
- Payment: {data.get('selectedPayment', 'Monthly')}
- Total: ${data['totalAmount']:,}

If you have questions, reply to this email.

Best regards,
BMJ-Machinery Marketing Solutions Team
        """
        content = Content("text/plain", plain_text_content)
        mail = Mail(from_email, to_email, subject, content)

        # Add CC if provided
        if cc_email_str and cc_email_str != from_email_str:
            mail.cc = [cc_email_str]

        # Attach PDF
        attachment = Attachment(
            FileContent(pdf_base64),
            FileName('bmj-marketing-proposal.pdf'),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        mail.attachment = attachment

        # Send email
        response = sg.send(mail)
        app.logger.info(f"SendGrid response: status={response.status_code}, body={response.body}")

        if response.status_code in [202, 250]:
            app.logger.info(f"Successfully sent proposal to {data['recipientEmail']}")
            return jsonify({'success': True, 'message': 'Proposal sent successfully with PDF attachment'})
        else:
            app.logger.error(f"SendGrid failed: {response.status_code} - {response.body}")
            return jsonify({'success': False, 'error': f'Email delivery failed (status {response.status_code}) - Check SendGrid logs'}), 500

    except Exception as e:
        app.logger.error(f"Error in send_proposal: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
