from flask import Flask, request, jsonify
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Cc
import os
from datetime import datetime
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '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')
SENDER_EMAIL = 'elena@neoticai.email'
SENDER_NAME = 'Elena from NeoticAI'
CC_EMAIL = 'work@neoticai.com'

print(f"✓ SENDGRID_API_KEY loaded: {SENDGRID_API_KEY[:10]}...")
print(f"✓ Sender: {SENDER_EMAIL}")
print(f"✓ CC: {CC_EMAIL}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'sender_email': SENDER_EMAIL
    })

@app.route('/api/send-proposal', methods=['POST'])
def send_proposal():
    """Send proposal email with PDF attachment"""
    try:
        data = request.json
        recipient_email = data.get('recipientEmail')
        
        # Transform frontend data to backend format
        selected_package = data.get('selectedPackage', {})
        selected_addons = data.get('selectedAddons', [])
        selected_frequency = data.get('selectedFrequency', 'monthly')
        total_monthly = data.get('totalMonthly', 0)
        
        # Calculate discount and payment details
        discount_rates = {'monthly': 0, 'quarterly': 0.05, 'annual': 0.15}
        discount = discount_rates.get(selected_frequency, 0) * 100
        discounted_monthly = total_monthly
        
        # Calculate first payment based on frequency
        if selected_frequency == 'monthly':
            first_payment = total_monthly
        elif selected_frequency == 'quarterly':
            first_payment = total_monthly * 3
        else:  # annual
            first_payment = total_monthly * 12
        
        # Calculate total prospects
        package_prospects = {
            'Growth Accelerator': 700,
            'Market Domination': 900,
            'Industry Leadership': 1300
        }
        prospects = package_prospects.get(selected_package.get('name', ''), 0)
        
        # Build proposal_data in expected format
        proposal_data = {
            'packageName': selected_package.get('name', ''),
            'monthlyTotal': selected_package.get('price', 0) + sum(addon.get('price', 0) for addon in selected_addons),
            'paymentTerm': selected_frequency,
            'discount': discount,
            'discountedMonthly': discounted_monthly,
            'firstPayment': first_payment,
            'addons': selected_addons,
            'prospects': prospects
        }
        
        print(f"\n📧 Processing email request...")
        print(f"To: {recipient_email}")
        print(f"Package: {proposal_data.get('packageName')}")
        
        # Generate PDF
        pdf_buffer = generate_pdf(proposal_data)
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        print(f"✓ PDF generated ({len(pdf_base64)} bytes)")
        
        # Create email body
        email_body = create_email_body(proposal_data)
        
        # Send via SendGrid
        message = Mail(
            from_email=Email(SENDER_EMAIL, SENDER_NAME),
            to_emails=To(recipient_email),
            subject=f"Custom Marketing Proposal for BMJ-Machinery - {proposal_data.get('packageName')}",
            html_content=email_body
        )
        
        # Add CC
        message.cc = [Cc(CC_EMAIL)]
        
        # Add PDF attachment
        message.attachment = [{
            'content': pdf_base64,
            'type': 'application/pdf',
            'filename': 'BMJ-Machinery-Proposal.pdf',
            'disposition': 'attachment'
        }]
        
        # Send email
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"✓ SendGrid response: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully via SendGrid',
                'service': 'sendgrid'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'SendGrid returned status {response.status_code}',
                'error': response.body
            }), 400
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'error': str(e)
        }), 500

def generate_pdf(proposal_data):
    """Generate PDF proposal"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a3b5c',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Marketing Proposal for BMJ-Machinery", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Package details
    story.append(Paragraph(f"<b>Selected Package:</b> {proposal_data.get('packageName')}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph(f"<b>Monthly Investment:</b> ${proposal_data.get('monthlyTotal', 0):,}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph(f"<b>Payment Term:</b> {proposal_data.get('paymentTerm').title()}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    if proposal_data.get('discount', 0) > 0:
        story.append(Paragraph(f"<b>Discount Applied:</b> {proposal_data.get('discount')}%", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>Discounted Monthly:</b> ${proposal_data.get('discountedMonthly', 0):,}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph(f"<b>First Payment:</b> ${proposal_data.get('firstPayment', 0):,}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Add-ons
    if proposal_data.get('addons') and len(proposal_data['addons']) > 0:
        story.append(Paragraph("<b>Selected Add-ons:</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        for addon in proposal_data['addons']:
            story.append(Paragraph(f"• {addon.get('name')} (+${addon.get('price'):,}/month)", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = f"<i>Proposal generated on {datetime.now().strftime('%B %d, %Y')}<br/>Contact: {SENDER_EMAIL}</i>"
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_email_body(proposal_data):
    """Create HTML email body"""
    addons_html = ""
    if proposal_data.get('addons') and len(proposal_data['addons']) > 0:
        addons_html = "<h3>Selected Add-ons:</h3><ul>"
        for addon in proposal_data['addons']:
            addons_html += f"<li>{addon.get('name')} (+${addon.get('price'):,}/month)</li>"
        addons_html += "</ul>"
    
    discount_html = ""
    if proposal_data.get('discount', 0) > 0:
        discount_html = f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Discount Applied:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{proposal_data.get('discount')}%</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Discounted Monthly:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">${proposal_data.get('discountedMonthly', 0):,}</td>
        </tr>
        """
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #1a3b5c;">Custom Marketing Proposal for BMJ-Machinery</h2>
            
            <p>Dear Chi Feng,</p>
            
            <p>Please find attached your customized marketing proposal for BMJ-Machinery. We've carefully crafted this solution based on your business objectives and growth targets.</p>
            
            <h3>Proposal Summary:</h3>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Selected Package:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{proposal_data.get('packageName')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Monthly Investment:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">${proposal_data.get('monthlyTotal', 0):,}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Payment Term:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{proposal_data.get('paymentTerm').title()}</td>
                </tr>
                {discount_html}
                <tr style="background: #f8f9fa;">
                    <td style="padding: 8px; font-weight: bold;"><strong>First Payment:</strong></td>
                    <td style="padding: 8px; font-weight: bold; color: #ff6b35;">${proposal_data.get('firstPayment', 0):,}</td>
                </tr>
            </table>
            
            {addons_html}
            
            <h3>Expected Outcomes:</h3>
            <ul>
                <li>Prospects Reached Monthly: {proposal_data.get('prospects', 0):,}+</li>
                <li>Multi-channel marketing execution</li>
                <li>Regular performance tracking and reporting</li>
                <li>Dedicated account management</li>
            </ul>
            
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Review the attached detailed proposal PDF</li>
                <li>Schedule a strategy call to discuss implementation</li>
                <li>Sign agreement and complete onboarding</li>
                <li>Launch campaigns within 2 weeks</li>
            </ol>
            
            <p>We're excited to partner with BMJ-Machinery and drive measurable growth for your business.</p>
            
            <p>Best regards,<br>
            <strong>{SENDER_NAME}</strong><br>
            NeoticAI Marketing Solutions<br>
            {SENDER_EMAIL}</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
            
            <p style="font-size: 0.9em; color: #666;">
                <em>This proposal is valid for 30 days from the date of issuance. All pricing and terms are subject to the signed service agreement.</em>
            </p>
        </div>
    </body>
    </html>
    """
    
    return html

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("\n🚀 Starting BMJ-Machinery Proposal Email Server...")
    print(f"📍 Server running on port {port}")
    print(f"📧 Emails will be sent from: {SENDER_EMAIL}")
    print(f"📋 CC: {CC_EMAIL}\n")
    app.run(debug=False, host='0.0.0.0', port=port)

