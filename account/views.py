from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from account.serializers import (
    SendPasswordResetEmailSerializer,
    UserChangePasswordSerializer,
    UserPasswordResetSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
)
from account.renderers import UserRenderer
from account.utils import send_jwt_token_response
from account.utils import email_test


class UserRegistrationView(APIView):
    """Register a new user"""
    renderer_classes = [UserRenderer]

    def post(self, request):
        # print("Incoming data:", request.data)
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token_data = send_jwt_token_response(user)
        return Response(
            {"data": token_data, "message": "Registration successful"},
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    """Authenticate user and return JWT tokens"""
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid email or password"]}
            )

        token_data = send_jwt_token_response(user)
        return Response(
            {"data": token_data, "message": "Login successful"},
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    """Return logged-in user profile"""
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(
            {"data": serializer.data, "message": "Profile fetched successfully"},
            status=status.HTTP_200_OK,
        )


class UserChangePasswordView(APIView):
    """Change current user's password"""
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class SendPasswordResetEmailView(APIView):
    """Send password reset link via email"""
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "Password reset link sent successfully. Please check your email."},
            status=status.HTTP_200_OK,
        )


class UserPasswordResetView(APIView):
    """Reset password using uid and token"""
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )


class ServerTest(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request):
        data, status_code = email_test()
        return Response(data, status=status_code)
