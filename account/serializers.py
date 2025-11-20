from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from account.models import User
from account.utils import Util

# from django.contrib.auth.password_validation import validate_password  # for password vaidation when creating new user and password validation
# throatle for preventing multiple unauthorized login attempts

# Helper function for matching passwords


def validate_passwords_match(password, password2):
    if password != password2:
        raise serializers.ValidationError(
            {"non_field_errors": [
                "Password and Confirm Password do not match"]}
        )
    return password


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "name", "password", "password2", "tc"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_tc(self, value):
        if value is False:
            raise serializers.ValidationError(
                "You must accept the Terms & Conditions.")
        return value

    def validate(self, attrs):
        # print("Serializer raw input:", attrs)
        password = attrs.get("password")
        password2 = attrs.get("password2")
        validate_passwords_match(password, password2)
        validate_password(password)
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Serializer for login validation"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for returning profile info"""
    class Meta:
        model = User
        fields = ["id", "email", "name"]


class UserChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context.get("user")
        password = attrs.get("password")
        password2 = attrs.get("password2")

        validate_passwords_match(password, password2)
        validate_password(password)

        user.set_password(password)
        user.save()
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    """Serializer for sending password reset email"""
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError(
                {"non_field_errors": ["No user found with this email address"]}
            )

        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        frontend_url = getattr(settings, "FRONTEND_URL",
                               "http://localhost:3000")
        reset_link = f"{frontend_url}/auth/reset_password/{uid}/{token}"

        body = f"""
            <p>Hello {user.name},</p>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">{reset_link}</a>
            <p>If you didn’t request this, please ignore this email.</p>
        """
        data = {
            "subject": "Reset Your Password",
            "body": body,
            "to_email": user.email,
        }
        Util.send_email(data)
        return attrs


class UserPasswordResetSerializer(serializers.Serializer):
    """Serializer for verifying token and resetting password"""
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = self.context.get("uid")
            token = self.context.get("token")
            password = attrs.get("password")
            password2 = attrs.get("password2")

            validate_passwords_match(password, password2)
            validate_password(password)

            user_id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError(
                    {"non_field_errors": ["Invalid or expired token"]}
                )

            user.set_password(password)
            user.save()
            return attrs

        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid or expired token"]}
            )
