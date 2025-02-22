import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Gmail's SMTP server details
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Your Gmail credentials
sender_email =  os.getenv('MAIL')
receiver_email =  os.getenv('MAIL')
password = os.getenv('GPASS')



def sendMail(subject='AI QUOTE : Failed',body='') :
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    # Connect to the Gmail SMTP server
    try:
        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)  # Login to your Gmail account
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send email
            print("Email sent successfully!")
    
    except Exception as e:
        print(f"Error sending email: {e}")
