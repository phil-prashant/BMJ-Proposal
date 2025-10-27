from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleProducer
import io
import base64

app = Flask(__name__)

# CORS setup to allow requests from frontend (fixes 403 preflight issues)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://bmj.neoticai.com", "http://localhost:3000"],  # Add local for dev if needed
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint - returns 200 if backend is running."""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/send-proposal', methods=['OPTIONS'])
def handle_options():
    """Handle CORS preflight requests explicitly."""
    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = 'https://bmj.neoticai.com'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response, 200

@app.route('/api/send-proposal', methods=['POST'])
def send_proposal():
    """Generate PDF proposal and send via SendGrid."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        # Extract required fields (with defaults for safety)
        firstname = data.get('firstname', 'Client')
        lastname = data.get('lastname', '')
        recipient_email = data.get('recipientEmail', '')
        selected_package_key = data.get('selectedPackage', '')
        package_details = data.get('packageDetails', {})
        selected_addons = data.get('selectedAddons', [])
        selected_payment = data.get('selectedPayment', 'monthly')
        total_amount = data.get('totalAmount', 0)

        if not recipient_email or '@' not in recipient_email:
            return jsonify({"success": False, "error": "Invalid email address"}), 400

        # Generate PDF with ReportLab
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 80, "Custom Marketing Proposal")
        p.setFont("Helvetica", 12)
        p.drawString(100, height - 100, f"Prepared for: {firstname} {lastname}")
        p.drawString(100, height - 120, f"Company: BMJ-Machinery Marketing Solutions")
        p.drawString(100, height - 140, f"Date: {os.environ.get('CURRENT_DATE', 'October 27, 2025')}")  # Optional env var for date

        # Package Details
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, height - 180, "Selected Package:")
        p.setFont("Helvetica", 12)
        p.drawString(100, height - 200, f"{package_details.get('name', 'N/A')}")
        p.drawString(100, height - 220, f"Base Price: ${package_details.get('price', 0):,}")

        # Deliverables
        y_pos = height - 240
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_pos, "Deliverables:")
        y_pos -= 20
        p.setFont("Helvetica", 10)
        for deliverable in package_details.get('deliverables', []):
            if y_pos < 100:  # Prevent overflow
                break
            p.drawString(120, y_pos, f"• {deliverable}")
            y_pos -= 15

        # Add-ons
        if selected_addons:
            y_pos -= 10
            p.setFont("Helvetica-Bold", 12)
            p.drawString(100, y_pos, "Selected Add-ons:")
            y_pos -= 20
            p.setFont("Helvetica", 10)
            for addon in selected_addons:
                if y_pos < 100:
                    break
                p.drawString(120, y_pos, f"• {addon.get('name', 'N/A')} - +${addon.get('price', 0)} ({addon.get('type', 'N/A')})")
                y_pos -= 15

        # Payment and Total
        y_pos -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_pos, "Payment Terms:")
        y_pos -= 15
        p.setFont("Helvetica", 10)
        p.drawString(120, y_pos, f"{selected_payment.replace('-', ' ').title()} - Total: ${total_amount:,}")
        y_pos -= 30

        # Terms Summary (abbreviated)
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_pos, "Terms & Conditions Summary:")
        y_pos -= 15
        p.setFont("Helvetica", 9)
        terms_summary = [
            "• Payment due upfront; services start post-clearance.",
            "• Monthly auto-renews; 30-day notice for longer terms.",
            "• No guarantees on results due to external factors.",
            "• Governed by US/EU laws; confidential.",
            "• Valid for 30 days. Contact for questions."
        ]
        for term in terms_summary:
            if y_pos < 100:
                break
            p.drawString(120, y_pos, term)
            y_pos -= 12

        # Footer
        p.setFont("Helvetica", 8)
        p.drawString(100, 50, "© 2025 Neotic AI Marketing & AI Solutions. Powered by NeoticAI.com")

        p.save()
        buffer.seek(0)

        # Prepare email attachment (base64 encode PDF)
        pdf_base64 = base64.b64encode(buffer.read()).decode()

        # Send via SendGrid
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        from_email = os.environ.get('FROM_EMAIL', 'elena@neoticai.email.com')
        cc_email = os.environ.get('CC_EMAIL', 'work@neoticai.com')

        message = Mail(
            from_email=from_email,
            to_emails=recipient_email,
            cc=[cc_email] if cc_email else None,
            subject=f'Your Custom Marketing Proposal - {firstname} {lastname}',
            html_content=f"""
            <html>
                <body>
                    <h2>Dear {firstname} {lastname},</h2>
                    <p>Thank you for your interest in BMJ-Machinery Marketing Solutions.</p>
                    <p>Attached is your personalized proposal based on your selections:</p>
                    <ul>
                        <li><strong>Package:</strong> {package_details.get('name', 'N/A')}</li>
                        <li><strong>Payment:</strong> {selected_payment.replace('-', ' ').title()}</li>
                        <li><strong>Total:</strong> ${total_amount:,}</li>
                        {''.join([f'<li><strong>Add-on:</strong> {addon.get("name", "N/A")} (+${addon.get("price", 0)})</li>' for addon in selected_addons]) if selected_addons else ''}
                    </ul>
                    <p>Next steps: Reply to confirm and arrange payment. This proposal is valid for 30 days.</p>
                    <p>Best regards,<br>Elena<br>Neotic AI Marketing & AI Solutions</p>
                </body>
            </html>
            """,
            attachments=[
                {
                    "content": pdf_base64,
                    "filename": f"proposal_{firstname}_{lastname}.pdf",
                    "type": "application/pdf",
                    "disposition": "attachment"
                }
            ]
        )

        response = sg.send(message)
        if response.status_code == 202:
            return jsonify({"success": True, "message": "Proposal sent successfully"}), 200
        else:
            return jsonify({"success": False, "error": f"SendGrid error: {response.status_code} - {response.body}"}), 500

    except Exception as e:
        print(f"Error in send_proposal: {str(e)}")  # Log for Railway
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # Production mode for Railway
