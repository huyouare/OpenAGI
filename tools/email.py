"""
tools/email.py

This file contains tools that allow the agent to send emails and verify email addresses.

"""

from core.tool import BaseTool, InputSpec, OutputSpec
import smtplib
import ssl
import os
import email
from sendgrid import SendGridAPIClient

class VerifyEmail(BaseTool):
    """Verifies the email is valid via SendGrid API."""
    def __init__(self):
        self.email: str = None
        self.sendgrid_api = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

    def description(self) -> str:
        return "Verifies the email is valid via SendGrid API."
    
    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("email", "The email to verify", "string"),
        ]
    
    def output_spec(self) -> list[OutputSpec]:
        return []
    
    def parse_input(self, input_str: str):
        self.email = input_str["email"]

    def run(self):
        data = {
            "email": self.email,
            "source": "signup"
        }

        try:
            response = self.sendgrid_api.client.validations.email.post(
                request_body=data
            )
        except Exception as e:
            print(e)

            # print(response.status_code)
            # print(response.body)
            # print(response.headers)

            # return {
            #     "output": response.body
            # }


class Email(BaseTool):
    def __init__(self):
        self.recipient: str = None
        self.subject: str = None
        self.body: str = None

    def description(self) -> str:
        return "Sends an email."
    
    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("recipient", "The recipient of the email", "string"),
            InputSpec("subject", "The subject of the email", "string"),
            InputSpec("body", "The body of the email", "string"),
        ]
    
    def output_spec(self) -> list[OutputSpec]:
        return []
    
    def parse_input(self, input_str: str):
        self.recipient = input_str["recipient"]
        self.subject = input_str["subject"]
        self.body = input_str["body"]

    def run(self):
        # Send the email
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "jessehu12@gmail.com"
        password = os.environ["EMAIL_PASSWORD"]
        message = email.message.EmailMessage()
        message["Subject"] = self.subject
        message["From"] = sender_email
        message["To"] = self.recipient
        message.set_content(self.body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(message)

        return {
            "output": f"Sent email to {self.recipient} with subject {self.subject} and body {self.body}",
        }

if __name__ == "__main__":
    # Test verifying email
    verify_email = VerifyEmail()
    verify_email.parse_input({
        "email": "jessehu12@gmail.com",
    })
    verify_email.run()


    # Test sending email
    email = Email()
    email.parse_input({
        "recipient": "huyouare@gmail.com",
        "subject": "Test",
        "body": "This is a test email.",
    })
    email.run()
