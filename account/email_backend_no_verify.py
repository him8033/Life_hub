import ssl
from django.core.mail.backends.smtp import EmailBackend

class NoVerifyEmailBackend(EmailBackend):
    """
    SMTP backend that disables SSL certificate verification.
    ONLY FOR LOCAL DEVELOPMENT.
    """
    def open(self):
        if self.connection:
            return False

        # Create SSL context that ignores verification
        self.ssl_context = ssl._create_unverified_context()

        return super().open()
