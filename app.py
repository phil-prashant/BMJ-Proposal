"""
Flask backend for BMJ-Machinery Marketing Proposal
Handles email sending via SendGrid API
"""

import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# SendGrid configuration
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_NAME = os.getenv('SENDER_NAME')


@app.route('/api/send-email', methods=['POST'])
def send_email():
    """
    Send proposal email with PDF attachment via SendGrid
    """
    try:
        data = request.json
        recipient_email = data.get('recipientEmail')
        proposal_data = data.get('proposalData', {})
        pdf_base64 = data.get('pdfBase64')
        
        if not recipient_email:
            return jsonify({'error': 'Recipient email is required'}), 400
        
        # Extract proposal details
        package_name = proposal_data.get('packageName', 'N/A')
        monthly_total = proposal_data.get('monthlyTotal', '0')
        payment_term = proposal_data.get('paymentTerm', 'N/A')
        first_payment = proposal_data.get('firstPayment', '0')
        prospects = proposal_data.get('prospects', 'N/A')
        
        # Create email content
        subject = f'BMJ-Machinery Marketing Proposal - {package_name} Package'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 8px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .summary {{
                    background: white;
                    padding: 20px;
                    border-radius: 6px;
                    border-left: 4px solid #06b6d4;
                    margin-bottom: 20px;
                }}
                .summary-item {{
                    padding: 10px 0;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .summary-item:last-child {{
                    border-bottom: none;
                }}
                .label {{
                    font-weight: 600;
                    color: #0f172a;
                    display: inline-block;
                    width: 150px;
                }}
                .value {{
                    color: #ea580c;
                    font-weight: 700;
                }}
                .footer {{
                    text-align: center;
                    color: #64748b;
                    font-size: 14px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #e2e8f0;
                }}
                .cta {{
                    background: #ea580c;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    display: inline-block;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Your Custom Marketing Proposal</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">BMJ-Machinery Growth Solution</p>
            </div>
            
            <div class="content">
                <p>Dear Eric / Chi Feng,</p>
                
                <p>Thank you for your interest in our marketing services. We've prepared a customized proposal based on your selections.</p>
                
                <div class="summary">
                    <div class="summary-item">
                        <span class="label">Selected Package:</span>
                        <span class="value">{package_name}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Monthly Investment:</span>
                        <span class="value">${monthly_total}/month</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Payment Term:</span>
                        <span>{payment_term}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">First Payment:</span>
                        <span class="value">${first_payment}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Expected Prospects:</span>
                        <span>{prospects} per month</span>
                    </div>
                </div>
                
                <p><strong>What's Next?</strong></p>
                <ul>
                    <li>Review the attached PDF proposal with complete details</li>
                    <li>Schedule a call to discuss your marketing strategy</li>
                    <li>Get started with our proven growth framework</li>
                </ul>
                
                <p>We're excited to help BMJ-Machinery achieve its growth objectives!</p>
            </div>
            
            <div class="footer">
                <p><strong>{SENDER_NAME}</strong></p>
                <p>{SENDER_EMAIL}</p>
                <p style="margin-top: 15px; font-size: 12px;">
                    This proposal is valid for 30 days from the date of this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Create message
        message = Mail(
            from_email=(SENDER_EMAIL, SENDER_NAME),
            to_emails=recipient_email,
            subject=subject,
            html_content=html_content
        )
        
        # Add PDF attachment if provided
        if pdf_base64:
            attachment = Attachment()
            attachment.file_content = FileContent(pdf_base64)
            attachment.file_type = FileType('application/pdf')
            attachment.file_name = FileName('BMJ-Machinery-Proposal.pdf')
            attachment.disposition = Disposition('attachment')
            message.attachment = attachment
        
        # Send email
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        return jsonify({
            'success': True,
            'message': 'Email sent successfully',
            'status_code': response.status_code
        }), 200
        
    except Exception as e:
        app.logger.error(f'Error sending email: {str(e)}')
        return jsonify({
            'error': 'Failed to send email',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'BMJ Proposal Email Service'
    }), 200


if __name__ == '__main__':
    # Check if required environment variables are set
    if not SENDGRID_API_KEY:
        print("ERROR: SENDGRID_API_KEY not found in environment variables")
        exit(1)
    if not SENDER_EMAIL:
        print("ERROR: SENDER_EMAIL not found in environment variables")
        exit(1)
    if not SENDER_NAME:
        print("ERROR: SENDER_NAME not found in environment variables")
        exit(1)
    
    print(f"Starting Flask server...")
    print(f"Sender: {SENDER_NAME} <{SENDER_EMAIL}>")
    app.run(host='0.0.0.0', port=5000, debug=True)
