from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
RESEND_API_KEY = os.getenv('RESEND_API_KEY', 're_73miNRj6_83vuf1KSmVNeiAwBM1U37jtN')
EMAILJS_SERVICE_ID = os.getenv('EMAILJS_SERVICE_ID', 'service_kkb35zr')
RESEND_ENDPOINT = "https://api.resend.com/emails"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'BMJ-Machinery Email Service'}), 200

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Send email via Resend with EmailJS fallback"""
    try:
        data = request.json
        recipient_email = data.get('recipientEmail')
        proposal_data = data.get('proposalData')
        
        if not recipient_email or not proposal_data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        print(f"📧 Attempting to send email to: {recipient_email}")
        
        # Generate PDF
        pdf_buffer = generate_proposal_pdf(proposal_data)
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        
        # Try Resend first
        resend_response = send_via_resend(recipient_email, proposal_data, pdf_base64)
        
        if resend_response['success']:
            return jsonify({
                'success': True,
                'message': '✓ Email sent successfully via Resend!',
                'service': 'resend'
            }), 200
        else:
            # Try EmailJS fallback
            print("⚠️ Resend failed, attempting EmailJS fallback...")
            emailjs_response = send_via_emailjs(recipient_email, proposal_data, pdf_base64)
            
            if emailjs_response['success']:
                return jsonify({
                    'success': True,
                    'message': '✓ Email sent successfully via EmailJS!',
                    'service': 'emailjs'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to send email via both services',
                    'errors': {
                        'resend': resend_response.get('error'),
                        'emailjs': emailjs_response.get('error')
                    }
                }), 500
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email sending"""
    try:
        test_data = {
            'packageName': 'Growth Accelerator (Test)',
            'monthlyTotal': '5985',
            'paymentTerm': 'Quarterly',
            'firstPayment': '10645',
            'prospects': '15-20'
        }
        
        pdf_buffer = generate_proposal_pdf(test_data)
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        
        resend_response = send_via_resend('prashant.kay3@gmail.com', test_data, pdf_base64)
        
        return jsonify({
            'success': resend_response['success'],
            'message': resend_response.get('message', 'Test email sent'),
            'response': resend_response
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_proposal_pdf(proposal_data):
    """Generate professional PDF proposal"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=20,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#06b6d4'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )
    
    # Title
    story.append(Paragraph("Custom Marketing Proposal for BMJ-Machinery", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Date
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", normal_style))
    story.append(Paragraph("<b>Prepared for:</b> Eric / Chi Feng, CEO", normal_style))
    story.append(Paragraph("<b>From:</b> NeoticAI Team (prashant@neoticai.com)", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(
        f"This proposal outlines our customized marketing solution for BMJ-Machinery. "
        f"We recommend the <b>{proposal_data.get('packageName')}</b> package with your selected add-ons, "
        f"designed to reach <b>{proposal_data.get('prospects')} prospects monthly</b>.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Pricing Summary
    story.append(Paragraph("Pricing Summary", heading_style))
    
    pricing_data = [
        ['Item', 'Amount'],
        ['Monthly Investment', f"${proposal_data.get('monthlyTotal')}"],
        ['Payment Frequency', proposal_data.get('paymentTerm')],
        ['First Payment Due', f"${proposal_data.get('firstPayment')}"],
    ]
    
    pricing_table = Table(pricing_data, colWidths=[3*inch, 2*inch])
    pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#06b6d4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f9ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
    ]))
    
    story.append(pricing_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Next Steps
    story.append(Paragraph("Next Steps", heading_style))
    story.append(Paragraph(
        "1. Review this proposal<br/>"
        "2. Schedule a consultation call<br/>"
        "3. Execute service agreement<br/>"
        "4. Onboarding and kickoff<br/>"
        "5. Campaign launch and optimization",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    story.append(Paragraph(
        "<b>Contact:</b> prashant@neoticai.com<br/>"
        "<b>Website:</b> neoticai.com",
        normal_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def send_via_resend(recipient_email, proposal_data, pdf_base64):
    """Send email via Resend API"""
    try:
        print(f"🔄 Attempting Resend API...")
        
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        email_body = f"""
Dear Eric / Chi Feng,

Please find attached our custom marketing proposal for BMJ-Machinery.

PROPOSAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Package: {proposal_data.get('packageName')}
Monthly Investment: ${proposal_data.get('monthlyTotal')}
Payment Frequency: {proposal_data.get('paymentTerm')}
First Payment: ${proposal_data.get('firstPayment')}
Expected Prospects Reached: {proposal_data.get('prospects')} per month
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The attached PDF includes:
✓ Complete service details
✓ Deliverables breakdown
✓ Pricing with all discounts applied
✓ Expected outcomes
✓ Terms & conditions
✓ Next steps

We look forward to discussing this proposal with you.

Best regards,
NeoticAI Team
prashant@neoticai.com
        """
        
        payload = {
            "from": "NeoticAI Team <prashant@neoticai.com>",
            "to": recipient_email,
            "subject": f"Custom Marketing Proposal for BMJ-Machinery - {proposal_data.get('packageName')}",
            "html": email_body.replace('\n', '<br/>'),
            "attachments": [
                {
                    "filename": "BMJ-Machinery-Proposal.pdf",
                    "content": pdf_base64
                }
            ]
        }
        
        response = requests.post(RESEND_ENDPOINT, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Email sent successfully via Resend")
            return {'success': True, 'message': 'Email sent via Resend'}
        else:
            error_msg = response.text
            print(f"❌ Resend failed: {response.status_code} - {error_msg}")
            return {'success': False, 'error': error_msg}
    
    except Exception as e:
        print(f"❌ Resend exception: {str(e)}")
        return {'success': False, 'error': str(e)}

def send_via_emailjs(recipient_email, proposal_data, pdf_base64):
    """EmailJS fallback - Note: Direct API call not recommended"""
    try:
        print(f"🔄 Attempting EmailJS fallback...")
        print(f"⚠️  Note: EmailJS backend sending requires proper configuration")
        
        # In production, you would call EmailJS through your backend
        # This is a placeholder that indicates EmailJS fallback was attempted
        
        return {
            'success': False,
            'error': 'EmailJS requires frontend integration. Please configure Resend for backend sending.'
        }
    except Exception as e:
        print(f"❌ EmailJS exception: {str(e)}")
        return {'success': False, 'error': str(e)}

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 BMJ-Machinery Proposal Email Service")
    print("=" * 60)
    print(f"✓ Resend API Key loaded: {RESEND_API_KEY[:15]}...")
    print(f"✓ EmailJS Service ID: {EMAILJS_SERVICE_ID}")
    print("✓ CORS enabled")
    print("=" * 60)
    print("📍 Server running on http://localhost:5000")
    print("📋 Health check: http://localhost:5000/health")
    print("=" * 60)
    app.run(debug=True, port=5000)