import threading
from django.core.mail import send_mail
from django.conf import settings

class EmailService:
    @staticmethod
    def send_async(subject, message, recipient_list):
        """
        Sends an email asynchronously using a background thread.
        This prevents the API from blocking while waiting for the SMTP server.
        """
        email_thread = threading.Thread(
            target=EmailService._send,
            args=(subject, message, recipient_list)
        )
        email_thread.start()

    @staticmethod
    def _send(subject, message, recipient_list, html_content=None):
        from django.core.mail import EmailMultiAlternatives
        
        try:
            print(f"Starting email thread for: {recipient_list}")
            
            email = EmailMultiAlternatives(
                subject,
                message, # plain text fallback
                settings.EMAIL_HOST_USER,
                recipient_list
            )
            
            if html_content:
                email.attach_alternative(html_content, "text/html")
                
            email.send(fail_silently=False)
            print(f"Email sent successfully to {recipient_list}")
        except Exception as e:
            print(f"Failed to send email to {recipient_list}: {e}")

    @staticmethod
    def send_html(subject, template_name, context, recipient_list):
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        email_thread = threading.Thread(
            target=EmailService._send,
            args=(subject, text_content, recipient_list, html_content)
        )
        email_thread.start()
