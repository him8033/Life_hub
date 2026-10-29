from django.core.mail import EmailMessage
from django.conf import settings
import os


class EmailService:
    """
    Email sending service with async-ready design.
    Currently synchronous but designed for future Celery integration.
    """

    @staticmethod
    def send_email(subject, body, to_email, from_email=None):
        """
        Send an email.

        Args:
            subject: Email subject
            body: Email body (HTML supported)
            to_email: Recipient email address
            from_email: Sender email (defaults to EMAIL_FROM)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            from_email = from_email or os.environ.get("EMAIL_FROM")

            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=[to_email]
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
            return True
        except Exception as e:
            # Log error in production
            print(f"Email sending failed: {e}")
            return False

    @staticmethod
    def send_otp_email(to_email, otp_code, purpose, expiry_minutes):
        """
        Send OTP email.

        Args:
            to_email: Recipient email
            otp_code: OTP code
            purpose: Purpose of OTP (e.g., 'email_verification')
            expiry_minutes: OTP expiry time in minutes
        """
        subject = f"Your {purpose.replace('_', ' ').title()} Code"

        body = f"""
        <h2>Your Verification Code</h2>
        <p>Your verification code is:</p>
        <h1 style="font-size: 32px; letter-spacing: 5px; color: #333;">{otp_code}</h1>
        <p>This code will expire in {expiry_minutes} minutes.</p>
        <p>If you didn't request this code, please ignore this email.</p>
        """

        return EmailService.send_email(subject, body, to_email)

    @staticmethod
    def send_verification_email(to_email, user_name, verification_link):
        """
        Send email verification email.

        Args:
            to_email: Recipient email
            user_name: User's name
            verification_link: Verification link
        """
        subject = "Verify Your Email Address"

        body = f"""
        <h2>Welcome to Life Hub!</h2>
        <p>Hello {user_name},</p>
        <p>Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
        <p>If you didn't create an account, please ignore this email.</p>
        """

        return EmailService.send_email(subject, body, to_email)

    @staticmethod
    def send_password_reset_email(to_email, user_name, reset_link):
        """
        Send password reset email.

        Args:
            to_email: Recipient email
            user_name: User's name
            reset_link: Password reset link
        """
        subject = "Reset Your Password"

        body = f"""
        <h2>Password Reset Request</h2>
        <p>Hello {user_name},</p>
        <p>We received a request to reset your password. Click the link below to reset it:</p>
        <p><a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>This link will expire in 15 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """

        return EmailService.send_email(subject, body, to_email)

    @staticmethod
    def send_welcome_email(to_email, user_name):
        """
        Send welcome email after successful registration.

        Args:
            to_email: Recipient email
            user_name: User's name
        """
        subject = "Welcome to Life Hub!"

        body = f"""
        <h2>Welcome to Life Hub!</h2>
        <p>Hello {user_name},</p>
        <p>Your account has been successfully created. Welcome to our community!</p>
        <p>You can now access all the features of Life Hub.</p>
        <p>If you have any questions, feel free to contact our support team.</p>
        """

        return EmailService.send_email(subject, body, to_email)

    @staticmethod
    def send_admin_welcome_email(to_email, user_name, password):
        """
        Send welcome email for admin-created users with password.

        Args:
            to_email: Recipient email
            user_name: User's name
            password: User's password
        """
        subject = "Welcome to Life Hub - Your Account Details"

        body = f"""
        <h2>Welcome to Life Hub!</h2>
        <p>Hello {user_name},</p>
        <p>Your account has been successfully created by an administrator. Welcome to our community!</p>
        
        <h3>Your Login Details:</h3>
        <p><strong>Email:</strong> {to_email}</p>
        <p><strong>Password:</strong> {password}</p>
        
        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; color: #856404;"><strong>⚠️ Important Security Notice:</strong></p>
            <p style="margin: 10px 0 0 0; color: #856404;">This is your temporary password. For your security, please change your password immediately after your first login.</p>
        </div>
        
        <p>You can now access all the features of Life Hub.</p>
        <p>If you have any questions, feel free to contact our support team.</p>
        """

        return EmailService.send_email(subject, body, to_email)

    @staticmethod
    def send_user_edit_email(to_email, changes, admin_email=None,):
        subject = ("Your Account Information Has Been Updated")
        changed_by = (admin_email or "Administrator")

        if changes:
            changes_html = "".join(
                f"<li>{change}</li>"
                for change in changes
            )

        else:
            changes_html = (
                "<li>Account information updated</li>"
            )

        body = f"""
        <h2>Account Update Notification</h2>

        <p>Hello,</p>

        <p>
            An administrator has updated
            your account information.
        </p>

        <p>
            <strong>Changes:</strong>
        </p>

        <ul>
            {changes_html}
        </ul>

        <p>
            <strong>Changed By:</strong>
            {changed_by}
        </p>

        <p>
            If you did not expect these changes
            or believe this was done incorrectly,
            please contact our support team.
        </p>
        """

        return EmailService.send_email(subject, body, to_email,)

    @staticmethod
    def send_status_change_email(to_email, old_status, new_status, reason="", admin_email=None,):
        subject = ("Your Account Status Has Been Updated")
        old_status_text = (old_status or "Not Set")
        new_status_text = (new_status or "Not Set")
        reason_text = (reason or "No reason provided")

        changed_by = (admin_email or "Administrator")

        body = f"""
        <h2>Account Status Updated</h2>

        <p>Hello,</p>

        <p>
            Your account status has been
            updated by an administrator.
        </p>

        <p>
            <strong>Previous Status:</strong>
            {old_status_text}
        </p>

        <p>
            <strong>New Status:</strong>
            {new_status_text}
        </p>

        <p>
            <strong>Reason:</strong>
            {reason_text}
        </p>

        <p>
            <strong>Changed By:</strong>
            {changed_by}
        </p>

        <p>
            If you have any questions about
            this change, please contact
            our support team.
        </p>
        """

        return EmailService.send_email(subject, body, to_email,)

    @staticmethod
    def send_delete_email(to_email, reason, admin_email,):

        subject = ("Your Account Has Been Deleted")
        reason_text = (reason or "No reason provided")

        body = f"""
        <h2>Account Deletion Notification</h2>

        <p>
            Your account has been deleted
            by an administrator.
        </p>

        <p>
            <strong>Reason:</strong>
            {reason_text}
        </p>

        <p>
            If you believe this is an error,
            please contact support immediately.
        </p>

        <p>
            <strong>Changed By:</strong>
            {admin_email}
        </p>
        """

        return EmailService.send_email(subject, body, to_email,)
