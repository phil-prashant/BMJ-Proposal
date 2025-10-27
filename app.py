from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleProducer
import io
import base64
import traceback
from datetime import datetime

app = Flask(__name__)

# CORS setup for frontend origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://bmj.neoticai.com", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/send-proposal', methods=['OPTIONS'])
def handle_options():
    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = 'https://bmj.neoticai.com'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response, 200

@app.route('/api/send-proposal', methods=['POST'])
def send_proposal():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400

        # Extract fields with safe defaults
        firstname = data.get('firstname', 'Client').strip()
        lastname = (data.get('lastname', '') or '').strip()  # Ensure empty string if None/missing
        recipient_email = data.get('recipientEmail', '').strip()
        selected_package_key = data.get('selectedPackage', '')
        package_details = data.get('packageDetails', {})
        selected_addons = data.get('selectedAddons', [])
        selected_payment = data.get('selectedPayment', 'monthly')
        total_amount = data.get('totalAmount', 0)
        client_name = data.get('clientName', f"{firstname} {lastname}").strip()

        if not recipient_email or '@' not in recipient_email:
            return jsonify({"success": False, "error": "Invalid email address"}), 400

        if not selected_package_key:
            return jsonify({"success": False, "error": "No package selected"}), 400

        # Load env vars early with defaults
        api_key = os.environ.get('SENDGRID_API_KEY')
        from_email = os.environ.get('FROM_EMAIL', 'elena@neoticai.email.com')
        cc_email = os.environ.get('CC_EMAIL', 'work@neoticai.com')
        current_date = os.environ.get('CURRENT_DATE', datetime.now().strftime('%B %d, %Y'))

        if not api_key:
            print("Error: SENDGRID_API_KEY missing in env vars")
            return jsonify({"success": False, "error": "Server configuration error: API key missing"}), 500

        print(f"Processing proposal for {client_name} ({recipient_email}). Package: {selected_package_key}, Total: ${total_amount}")

        # Generate PDF using ReportLab
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y_position = height - 80

        # Header
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredText(width / 2, y_position, "Custom Marketing Proposal")
        y_position -= 30
        p.setFont("Helvetica", 12)
        p.drawCentredText(width / 2, y_position, f"Prepared for: {firstname} {lastname}")
        y_position -= 20
        p.drawCentredText(width / 2, y_position, "BMJ-Machinery Marketing Solutions")
        y_position -= 20
        p.drawCentredText(width / 2, y_position, f"Date: {current_date}")
        y_position -= 40

        # Selected Package
        p.setFont("Helvetica-Bold", 14)
        p.drawString(72, y_position, "Selected Package:")
        y_position -= 20
        p.setFont("Helvetica", 12)
        package_name = package_details.get('name', selected_package_key)
        p.drawString(72, y_position, f"{package_name} - ${package_details.get('price', 0):,}")
        y_position -= 20

        # Deliverables
        if 'deliverables' in package_details:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(72, y_position, "Deliverables:")
            y_position -= 15
            p.setFont("Helvetica", 10)
            for deliverable in package_details['deliverables']:
                if y_position < 100:  # New page if needed
                    p.showPage()
                    p.setFont("Helvetica", 10)
                    y_position = height - 50
                p.drawString(72, y_position, f"• {deliverable}")
                y_position -= 15
            if 'youtubeNote' in package_details:
                y_position -= 5
                p.drawString(72, y_position, f"Note: {package_details['youtubeNote']}")
                y_position -= 20

        # Add-ons
        if selected_addons:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(72, y_position, "Selected Add-ons:")
            y_position -= 15
            p.setFont("Helvetica", 10)
            for addon in selected_addons:
                if y_position < 100:
                    p.showPage()
                    y_position = height - 50
                addon_name = addon.get('name', 'Unknown Add-on')
                addon_price = addon.get('price', 0)
                p.drawString(72, y_position, f"• {addon_name} - +${addon_price:,} ({addon.get('type', 'monthly')})")
                y_position -= 15

        # Payment Terms
        y_position -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(72, y_position, "Payment Terms:")
        y_position -= 15
        p.setFont("Helvetica", 10)
        payment_label = f"{selected_payment.title()} - Total: ${total_amount:,}"
        p.drawString(72, y_position, payment_label)
        y_position -= 20

        # Terms Summary
        p.setFont("Helvetica-Bold", 12)
        p.drawString(72, y_position, "Key Terms:")
        y_position -= 15
        p.setFont("Helvetica", 9)
        terms_summary = [
            "• Services commence after payment. All work is DFY.",
            "• Client provides assets within 5 days; approvals required.",
            "• Monthly auto-renews; 30 days notice for longer terms.",
            "• No performance guarantees due to external factors.",
            "• Full terms in the agreement. Valid for 30 days."
        ]
        for term in terms_summary:
            if y_position < 100:
                p.showPage()
                y_position = height - 50
            p.drawString(72, y_position, term)
            y_position -= 12
        y_position -= 20

        # Footer
        p.setFont("Helvetica", 9)
        p.drawCentredText(width / 2, 50, "© 2025 Neotic AI Marketing & AI Solutions. Confidential.")
        p.drawCentredText(width / 2, 35, "Powered by NeoticAI.com")

        p.save()
        buffer.seek(0)
        pdf_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        # Prepare email
        message = Mail(
            from_email=from_email,
            to_emails=recipient_email,
            subject=f"Custom Marketing Proposal for {client_name} - BMJ Machinery Solutions",
            html_content=f"""
            <h2>Dear {firstname} {lastname},</h2>
            <p>Thank you for your interest in BMJ-Machinery Marketing Solutions. Attached is your customized proposal based on your selections.</p>
            <ul>
                <li><strong>Package:</strong> {package_name}</li>
                <li><strong>Total Amount:</strong> ${total_amount:,} ({selected_payment})</li>
                <li><strong>Add-ons:</strong> {len(selected_addons)} selected</li>
            </ul>
            <p>Please review the attached PDF for full details, deliverables, and terms. Contact us to proceed.</p>
            <p>Best regards,<br>BMJ Team<br>elena@neoticai.email.com</p>
            """
        )

        # Attach PDF
        attachment = Attachment(
            FileContent(pdf_base64),
            FileName(f"BMJ_Proposal_{firstname}_{lastname}_{current_date.replace(' ', '_')}.pdf"),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        message.attachment = attachment

        # Send via SendGrid
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        if response.status_code == 202:
            print(f"Email sent successfully to {recipient_email} (CC: {cc_email if cc_email != from_email else 'None'})")
            # Optional: Add CC by creating a separate send if needed, but SendGrid supports cc in Mail
            if cc_email and cc_email != from_email:
                cc_message = Mail(
                    from_email=from_email,
                    to_emails=cc_email,
                    subject=message.subject,
                    html_content=f"<p>CC: Proposal sent to {recipient_email}</p>{message.html_content}",
                    attachments=[attachment]
                )
                sg.send(cc_message)
                print(f"CC email sent to {cc_email}")

            return jsonify({"success": True, "message": "Proposal sent successfully"}), 200
        else:
            error_body = response.body.decode('utf-8')
            print(f"SendGrid error: {response.status_code} - {error_body}")
            return jsonify({"success": False, "error": f"Email send failed: {response.status_code} - {error_body}"}), 500

    except Exception as e:
        error_msg = str(e)
        print(f"Unexpected error in send_proposal: {error_msg}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": f"Internal server error: {error_msg}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
