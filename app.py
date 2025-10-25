# BMJ-Machinery Proposal Email Server
# Handles email sending via Resend with EmailJS fallback

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
from io import BytesIO
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys
RESEND_API_KEY = os.getenv('RESEND_API_KEY', 're_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN')
EMAILJS_SERVICE_ID = os.getenv('EMAILJS_SERVICE_ID', 'service_kkb35zr')
EMAILJS_TEMPLATE_ID = os.getenv('EMAILJS_TEMPLATE_ID', 'template_dbqjamx')
EMAILJS_PUBLIC_KEY = os.getenv('EMAILJS_PUBLIC_KEY', 'lWcX2ZAuSeQUVvyNk')

RESEND_ENDPOINT = "https://api.resend.com/emails"
EMAILJS_ENDPOINT = "https://api.emailjs.com/api/v1.0/email/send"

print("="*60)
print("BMJ-Machinery Proposal Email Server")
print("="*60)
print(f"✓ Resend API Key loaded: {RESEND_API_KEY[:10]}...")
print(f"✓ EmailJS Service ID: {EMAILJS_SERVICE_ID}")
print(f"✓ CORS enabled")
print("="*60)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'BMJ-Machinery Email Server'
    })

@app.route('/api/send-email', methods=['POST', 'OPTIONS'])
def send_email():
    """
    Send proposal email
    
    Request body:
    {
        "recipientEmail": "recipient@example.com",
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
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        recipient_email = data.get('recipientEmail', '').strip()
        proposal_data = data.get('proposalData', {})
        
        # Validate email
        if not recipient_email or '@' not in recipient_email:
            return jsonify({
                'success': False,
                'message': 'Invalid recipient email address'
            }), 400
        
        print(f"\n📧 Email Request: {recipient_email}")
        print(f"📦 Package: {proposal_data.get('packageName')}")
        
        # Try Resend first
        print("→ Attempting Resend...")
        resend_result = send_via_resend(recipient_email, proposal_data)
        
        if resend_result['success']:
            print(f"✓ Success via Resend!\n")
            return jsonify(resend_result), 200
        
        # Fallback to EmailJS
        print("→ Resend failed, attempting EmailJS fallback...")
        emailjs_result = send_via_emailjs(recipient_email, proposal_data)
        
        if emailjs_result['success']:
            print(f"✓ Success via EmailJS (fallback)!\n")
            return jsonify(emailjs_result), 200
        
        # Both failed
        print(f"✗ Both services failed\n")
        return jsonify({
            'success': False,
            'message': 'Failed to send email via both services',
            'resend_error': resend_result.get('error'),
            'emailjs_error': emailjs_result.get('error')
        }), 500
    
    except Exception as e:
        print(f"✗ Server error: {str(e)}\n")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'error': str(e)
        }), 500

def send_via_resend(recipient_email, proposal_data):
    """Send email via Resend API (Primary service)"""
    try:
        # Build email body
        email_body = build_email_body(proposal_data)
        
        # Build headers
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Build payload
        payload = {
            "from": "NeoticAI Team <prashant@neoticai.com>",
            "to": recipient_email,
            "subject": f"Custom Marketing Proposal for BMJ-Machinery - {proposal_data.get('packageName', 'Proposal')}",
            "html": email_body,
            "reply_to": "prashant@neoticai.com"
        }
        
        print(f"  Sending to: {recipient_email}")
        print(f"  Subject: {payload['subject']}")
        
        # Make request
        response = requests.post(
            RESEND_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            return {
                'success': True,
                'message': 'Email sent successfully via Resend!',
                'service': 'resend',
                'email_id': response_data.get('id'),
                'recipient': recipient_email
            }
        else:
            print(f"  Error: {response.text[:200]}")
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }
    
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Resend API timeout'
        }
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def send_via_emailjs(recipient_email, proposal_data):
    """Send email via EmailJS API (Fallback service)"""
    try:
        # Build email body
        email_body = build_email_body(proposal_data)
        
        # EmailJS payload format
        payload = {
            "service_id": EMAILJS_SERVICE_ID,
            "template_id": EMAILJS_TEMPLATE_ID,
            "user_id": EMAILJS_PUBLIC_KEY,
            "template_params": {
                "from_email": "prashant@neoticai.com",
                "from_name": "NeoticAI Team",
                "to_email": recipient_email,
                "to_name": "Chi Feng",
                "subject": f"Custom Marketing Proposal for BMJ-Machinery - {proposal_data.get('packageName', 'Proposal')}",
                "email_body": email_body,
                "package_name": proposal_data.get('packageName', 'N/A'),
                "monthly_total": f"${proposal_data.get('monthlyTotal', '0')}",
                "first_payment": f"${proposal_data.get('firstPayment', '0')}",
                "payment_term": proposal_data.get('paymentTerm', 'Monthly'),
                "discount": f"{proposal_data.get('discount', '0')}%",
                "leads": proposal_data.get('leads', '15-20'),
                "meetings": proposal_data.get('meetings', '8-12'),
                "traffic": proposal_data.get('traffic', '30-40%')
            }
        }
        
        print(f"  Sending to: {recipient_email}")
        print(f"  Subject: {payload['template_params']['subject']}")
        
        # Make request
        response = requests.post(
            EMAILJS_ENDPOINT,
            json=payload,
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Email sent successfully via EmailJS!',
                'service': 'emailjs',
                'recipient': recipient_email
            }
        else:
            print(f"  Error: {response.text[:200]}")
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }
    
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'EmailJS API timeout'
        }
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def build_email_body(proposal_data):
    """Build professional HTML email body"""
    
    package_name = proposal_data.get('packageName', 'N/A')
    monthly_total = proposal_data.get('monthlyTotal', 0)
    first_payment = proposal_data.get('firstPayment', 0)
    payment_term = proposal_data.get('paymentTerm', 'Monthly')
    discount = proposal_data.get('discount', 0)
    add_ons = proposal_data.get('addOns', [])
    leads = proposal_data.get('leads', '15-20')
    meetings = proposal_data.get('meetings', '8-12')
    traffic = proposal_data.get('traffic', '30-40%')
    
    add_ons_html = ''
    if add_ons:
        add_ons_html = '<ul>' + ''.join([f'<li>{addon}</li>' for addon in add_ons]) + '</ul>'
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #1a202c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .section {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #0891b2; }}
            .section h2 {{ margin-top: 0; color: #1a202c; font-size: 16px; }}
            .pricing {{ background: #e0f7ff; padding: 15px; border-radius: 8px; margin: 15px 0; }}
            .pricing p {{ margin: 5px 0; font-size: 14px; }}
            .price-highlight {{ font-size: 20px; font-weight: bold; color: #0891b2; margin: 10px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; }}
            ul {{ margin: 10px 0; padding-left: 20px; }}
            li {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Custom Marketing Proposal</h1>
                <p>For BMJ-Machinery</p>
            </div>
            
            <p>Dear Eric / Chi Feng,</p>
            
            <p>Thank you for your interest in NeoticAI's marketing services. Please find below your custom proposal tailored specifically for BMJ-Machinery.</p>
            
            <div class="section">
                <h2>📦 Selected Package</h2>
                <p><strong>{package_name}</strong></p>
                <p>Comprehensive lead generation and marketing foundation with integrated digital strategies.</p>
            </div>
            
            <div class="pricing">
                <p><strong>Package Details:</strong></p>
                <p>Monthly Investment: <strong>${monthly_total:,.2f}</strong></p>
                <p>Payment Term: <strong>{payment_term}</strong></p>
                {f'<p>Discount Applied: <strong>{discount}%</strong></p>' if discount > 0 else ''}
                <div class="price-highlight">First Payment: ${first_payment:,.2f}</div>
            </div>
            
            {f'''<div class="section">
                <h2>✨ Add-ons Included</h2>
                {add_ons_html}
            </div>''' if add_ons_html else ''}
            
            <div class="section">
                <h2>📊 Expected Outcomes</h2>
                <p>✓ <strong>{leads} qualified leads per month</strong></p>
                <p>✓ <strong>{meetings} estimated meetings per month</strong></p>
                <p>✓ <strong>{traffic} website traffic increase</strong></p>
                <p>✓ Professional brand positioning</p>
                <p>✓ Improved sales-ready prospects</p>
            </div>
            
            <div class="section">
                <h2>🎯 Next Steps</h2>
                <p>1. Review this proposal thoroughly</p>
                <p>2. Schedule a consultation call with our team</p>
                <p>3. Finalize contract and payment terms</p>
                <p>4. Kick-off your marketing transformation!</p>
            </div>
            
            <p>We're excited to partner with BMJ-Machinery and drive meaningful growth for your business.</p>
            
            <div class="footer">
                <p>NeoticAI Team</p>
                <p>Email: prashant@neoticai.com</p>
                <p>Website: www.neoticai.com</p>
                <p style="margin-top: 15px; font-size: 11px;">© 2025 NeoticAI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test endpoint to send test email"""
    try:
        test_data = {
            'recipientEmail': 'prashant.kay3@gmail.com',
            'proposalData': {
                'packageName': 'Growth Accelerator',
                'monthlyTotal': 5985,
                'firstPayment': 10645,
                'paymentTerm': 'Quarterly',
                'discount': 5,
                'addOns': ['Analytics Dashboard', 'Dedicated Copywriter'],
                'leads': '15-20',
                'meetings': '8-12',
                'traffic': '30-40%'
            }
        }
        
        print("\n🧪 TEST EMAIL")
        print(f"Sending test email to: {test_data['recipientEmail']}")
        
        # Try Resend
        resend_result = send_via_resend(test_data['recipientEmail'], test_data['proposalData'])
        
        if resend_result['success']:
            return jsonify({
                'success': True,
                'message': 'Test email sent successfully via Resend!',
                'result': resend_result
            }), 200
        
        # Fallback to EmailJS
        emailjs_result = send_via_emailjs(test_data['recipientEmail'], test_data['proposalData'])
        
        if emailjs_result['success']:
            return jsonify({
                'success': True,
                'message': 'Test email sent successfully via EmailJS!',
                'result': emailjs_result
            }), 200
        
        return jsonify({
            'success': False,
            'message': 'Test email failed',
            'resend': resend_result,
            'emailjs': emailjs_result
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("\n🚀 Starting BMJ-Machinery Proposal Email Server...")
    print(f"📍 Server running on http://localhost:5000")
    print("📝 Available endpoints:")
    print("   - POST /api/send-email (Send proposal email)")
    print("   - GET  /health (Health check)")
    print("   - POST /api/test-email (Send test email)")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
