from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from cloudinary.utils import cloudinary_url
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import send_mail
import ssl
import os


def send_jwt_token_response(user):
    """Generate JWT tokens and return dict."""
    refresh = RefreshToken.for_user(user)

    # PROFILE IMAGE
    profile_image_url = None

    if hasattr(user, "profile") and user.profile.public_id:

        url, _ = cloudinary_url(
            user.profile.public_id,
            width=300,
            height=300,
            crop="fill",
            gravity="face",
            quality="auto",
            fetch_format="auto"
        )

        profile_image_url = url

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),

        "user": {
            "id": user.id,
            "email": user.email,

            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,

            "role": user.role,
            "is_verified": user.is_verified,

            # image
            "profile_image": profile_image_url,
        },
    }


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            from_email=os.environ.get("EMAIL_FROM"),
            to=[data["to_email"]]
        )
        # email.send()
        email.content_subtype = "html"  # allows HTML emails
        email.send(fail_silently=False)


def email_test():
    try:
        send_mail(
            subject="Test Email Subject",
            message="This is a test email message.",
            from_email=os.environ.get("EMAIL_FROM"),
            recipient_list=["ak9132152@gmail.com"],
            fail_silently=False,
        )
        return {"message": "Test email sent successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
