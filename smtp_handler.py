import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF
from datetime import datetime
from email.mime.base import MIMEBase
from email import encoders

def send_email(to_email, subject, body, attachment_path=None):
    sender_email = ""
    sender_password = ""

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    msg.attach(MIMEText(body, 'html'))

    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={attachment_path}",
        )
        msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        return False
    
def send_welcome_email(to_email):
    subject = "Welcome to ExpenseFlow - Your Financial Journey Starts Here!"
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: auto;
            }}
            h2 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            p {{
                color: #555;
                font-size: 16px;
                line-height: 1.6;
            }}
            .cta {{
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
                font-size: 16px;
            }}
            .cta:hover {{
                background-color: #2980b9;
            }}
            .footer {{
                margin-top: 30px;
                color: #777;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to ExpenseFlow!</h2>
            <p>Hi there,</p>
            <p>We're thrilled to have you join ExpenseFlow, your go-to tool for managing finances effortlessly. Whether you're tracking expenses, monitoring income, or planning budgets, we're here to make it simple and intuitive.</p>
            <p>Get started today and take control of your financial journey!</p>
            <a href="http://yourwebsite.com/login" class="cta">Go to Dashboard</a>
            <div class="footer">
                <p>If you have any questions, feel free to <a href="mailto:support@expenseflow.com" style="color: #3498db;">contact us</a>.</p>
                <p>Best regards,<br><strong>The ExpenseFlow Team</strong></p>
                <p style="font-size: 12px; color: #999;">You're receiving this email because you signed up for ExpenseFlow. <a href="#" style="color: #3498db;">Unsubscribe</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_password_change_email(to_email):
    subject = "Your ExpenseFlow Password Has Been Updated"
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: auto;
            }}
            h2 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            p {{
                color: #555;
                font-size: 16px;
                line-height: 1.6;
            }}
            .cta {{
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
                font-size: 16px;
            }}
            .cta:hover {{
                background-color: #2980b9;
            }}
            .footer {{
                margin-top: 30px;
                color: #777;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Password Updated Successfully</h2>
            <p>Hi there,</p>
            <p>Your ExpenseFlow account password has been successfully updated. If you did not make this change, please contact us immediately to secure your account.</p>
            <a href="http://yourwebsite.com/login" class="cta">Login to Your Account</a>
            <div class="footer">
                <p>If you have any questions, feel free to <a href="mailto:support@expenseflow.com" style="color: #3498db;">contact us</a>.</p>
                <p>Best regards,<br><strong>The ExpenseFlow Team</strong></p>
                <p style="font-size: 12px; color: #999;">You're receiving this email because your password was updated. <a href="#" style="color: #3498db;">Unsubscribe</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_dashboard_reset_email(to_email):
    subject = "Your ExpenseFlow Dashboard Has Been Reset"
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: auto;
            }}
            h2 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            p {{
                color: #555;
                font-size: 16px;
                line-height: 1.6;
            }}
            .cta {{
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
                font-size: 16px;
            }}
            .cta:hover {{
                background-color: #2980b9;
            }}
            .footer {{
                margin-top: 30px;
                color: #777;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Dashboard Reset Successfully</h2>
            <p>Hi there,</p>
            <p>Your ExpenseFlow dashboard has been successfully reset. All transactions have been cleared. If you did not perform this action, please contact us immediately to secure your account.</p>
            <a href="http://yourwebsite.com/login" class="cta">Login to Your Account</a>
            <div class="footer">
                <p>If you have any questions, feel free to <a href="mailto:support@expenseflow.com" style="color: #3498db;">contact us</a>.</p>
                <p>Best regards,<br><strong>The ExpenseFlow Team</strong></p>
                <p style="font-size: 12px; color: #999;">You're receiving this email because your dashboard was reset. <a href="#" style="color: #3498db;">Unsubscribe</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_otp_email(to_email):
    otp = generate_otp()
    subject = "Your OTP for ExpenseFlow - Secure Your Account"
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: auto;
            }}
            h2 {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            p {{
                color: #555;
                font-size: 16px;
                line-height: 1.6;
            }}
            .otp {{
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 24px;
                display: inline-block;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                color: #777;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Your One-Time Password (OTP)</h2>
            <p>Hi there,</p>
            <p>You requested an OTP to secure your ExpenseFlow account. Here is your OTP:</p>
            <div class="otp">{otp}</div>
            <p>This OTP is valid for <strong>5 minutes</strong>. Please do not share it with anyone.</p>
            <div class="footer">
                <p>If you did not request this OTP, please contact us immediately at <a href="mailto:support@expenseflow.com" style="color: #3498db;">support@expenseflow.com</a>.</p>
                <p>Best regards,<br><strong>The ExpenseFlow Team</strong></p>
                <p style="font-size: 12px; color: #999;">You're receiving this email because an OTP was requested for your account. <a href="#" style="color: #3498db;">Unsubscribe</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, body), otp

def generate_transactions_pdf(transactions, user_email):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="ExpenseFlow - All Transactions", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"User: {user_email}", ln=True, align="L")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=10, style="B")
    pdf.cell(40, 10, "Date", border=1)
    pdf.cell(40, 10, "Category", border=1)
    pdf.cell(50, 10, "Remark", border=1)
    pdf.cell(30, 10, "Type", border=1)
    pdf.cell(30, 10, "Amount", border=1)
    pdf.ln()
    pdf.set_font("Helvetica", size=10)
    for transaction in transactions:
        amount = f"{transaction['amount']:.2f}"
        pdf.cell(40, 10, str(transaction['date']), border=1)
        pdf.cell(40, 10, transaction['category'], border=1)
        pdf.cell(50, 10, transaction['remark'] or "-", border=1)
        pdf.cell(30, 10, transaction['type'], border=1)
        pdf.cell(30, 10, amount, border=1)
        pdf.ln()
    pdf_filename = f"transactions_{user_email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

def generate_otp():
    return random.randint(1000, 9999)