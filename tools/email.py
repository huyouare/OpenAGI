"""
tools/email.py

This file contains tools that allow the agent to send emails and verify email addresses.

VerifyEmail only works when subscribed to SendGrid Pro.
"""

from core.tool import BaseTool, InputSpec, OutputSpec
import os
import email
from sendgrid import SendGridAPIClient
from python_http_client.exceptions import HTTPError
from sendgrid.helpers.mail import Mail, Email, To, Content

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

        response = self.sendgrid_api.client.validations.email.post(
            request_body=data
        )

        print(response.status_code)
        print(response.body)
        print(response.headers)

        return {
            "output": response.body
        }


class SendEmail(BaseTool):
    """Send an email using the SendGrid API."""
    def __init__(self):
        self.sender_email: str = None
        self.receiver_email: str = None
        self.subject: str = None
        self.body: str = None
        self.sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

    def description(self) -> str:
        return "Send an email using the SendGrid API."
    
    def input_spec(self) -> list[InputSpec]:
        return [
            InputSpec("sender_email", "The sender email", "string"),
            InputSpec("receiver_email", "The receiver email", "string"),
            InputSpec("subject", "The subject of the email", "string"),
            InputSpec("body", "The body of the email", "string"),
        ]
    
    def output_spec(self) -> list[OutputSpec]:
        return []
    
    def parse_input(self, input_str: str):
        self.sender_email = input_str["sender_email"]
        self.receiver_email = input_str["receiver_email"]
        self.subject = input_str["subject"]
        self.body = input_str["body"]

    def run(self):
        from_email = Email(self.sender_email)  # Change to your verified sender
        to_email = To("huyouare@gmail.com")  # Always send to myself for now
        subject = self.subject
        content = Content("text/plain", self.body)
        mail = Mail(from_email, to_email, subject, content)

        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()
        print(f"""Sending email...
To: {self.receiver_email}
From {self.sender_email}
Subject:\n{self.subject}
Body:\n{self.body}""")

        # Send an HTTP POST request to /mail/send
        try:
            response = self.sg.client.mail.send.post(request_body=mail_json)
            return { "output": response.body }
        except HTTPError as e:
            print("Sendgrid error:", e.to_dict)
            return { "output": str(e.to_dict) }


if __name__ == "__main__":
    # # Test verifying email
    # verify_email = VerifyEmail()
    # verify_email.parse_input({
    #     "email": "jessehu12@gmail.com",
    # })
    # verify_email.run()

    # Test sending email
    send_email = SendEmail()
    send_email.parse_input({
        "sender_email": "jessehu12@gmail.com",
        "receiver_email": "huyouare@gmail.com",
        "subject": "Test email",
        "body": "This is a test email.",
    })
    send_email.run()
