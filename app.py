import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Cc, Content, Attachment, FileContent, FileName, FileType, Disposition

app = Flask(__name__)
CORS(app)

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'elena@neoticai.email.com')
SENDER_NAME = os.environ.get('SENDER_NAME', 'Elena from NeoticAI')
CC_EMAIL = os.environ.get('CC_EMAIL', 'work@neoticai.com')

@app.route('/api/health')
def health():
    return jsonify(status='healthy')

@app.route('/api/send-proposal', methods=['POST'])
def send_proposal():
    data = request.json
    recipient_email = data['recipientEmail']
    package = data.get('package')
    add_ons = data.get('addOns', [])
    payment = data.get('payment')
    summary = data.get('summary', '')

    # Compose email
    subject = "Custom Marketing Proposal for BMJ-Machinery"
    html = f"""
    <h2>BMJ-Machinery Proposal</h2>
    <b>Package:</b> {package}<br>
    <b>Add-Ons:</b> {', '.join(add_ons)}<br>
    <b>Payment Term:</b> {payment}<br>
    <br />
    {summary}
    <hr>
    <small>Sent from NeoticAI Proposal Dashboard</small>
    """

    mail = Mail(
        from_email=Email(SENDER_EMAIL, SENDER_NAME),
        to_emails=[To(recipient_email)],
        subject=subject,
        html_content=html
    )
    mail.cc = [Cc(CC_EMAIL)]

    # Send via SendGrid
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)
        return jsonify(success=True, status=response.status_code)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)
