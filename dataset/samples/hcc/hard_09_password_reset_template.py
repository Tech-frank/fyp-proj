from django.core.mail import send_mail
from django.template.loader import render_to_string

password_reset_template = "accounts/emails/password_reset.html"
password_reset_subject = "Reset your password"


def send_reset_email(user, link):
    html = render_to_string(password_reset_template, {"user": user, "link": link})
    send_mail(password_reset_subject, "", "noreply@example.com", [user.email], html_message=html)
