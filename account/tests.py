from django.test import TestCase
from unittest.mock import patch
from account.models import User, OTP, OTPPurpose, UserStatus, Role, Permission, RolePermission, UserRole
from account.services.otp_service import OTPService
from account.services.auth_service import AuthService
from account.serializers.user import (
    PasswordForgotSerializer,
    OTPVerificationSerializer,
    PasswordResetSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
)


class OTPVerificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_user@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="User"
        )
        self.purpose, _ = OTPPurpose.objects.get_or_create(
            slug="forgot_password",
            defaults={
                "name": "Forgot Password",
                "description": "Password reset OTP",
                "expiry_seconds": 900,
                "max_attempts": 3,
                "resend_cooldown_seconds": 60,
                "is_active": True,
            }
        )

    @patch("account.models.otp.OTP.generate_code", return_value="654321")
    @patch("account.services.email_service.EmailService.send_otp_email", return_value=True)
    def test_otp_incorrect_first_attempt_then_correct_second_attempt(self, mock_email, mock_code):
        # 1. Request forgot password OTP
        s1 = PasswordForgotSerializer(data={"email": self.user.email})
        self.assertTrue(s1.is_valid(), s1.errors)
        reset_token = s1.validated_data.get("reset_token")
        self.assertTrue(bool(reset_token))

        # Retrieve generated OTP record
        otp = OTP.objects.filter(user=self.user, purpose=self.purpose, is_used=False).order_by("-created_at").first()
        self.assertIsNotNone(otp)

        real_code = "654321"

        # 2. First attempt with incorrect OTP
        wrong_code = "000000" if real_code != "000000" else "111111"
        v1 = OTPVerificationSerializer(data={
            "email": self.user.email,
            "otp_code": wrong_code,
            "purpose": "forgot_password",
            "reset_token": reset_token,
        })
        self.assertFalse(v1.is_valid())
        self.assertIn("non_field_errors", v1.errors)
        err_msg = str(v1.errors["non_field_errors"][0])
        self.assertIn("2 attempts remaining", err_msg)

        # Verify OTP is not consumed
        otp.refresh_from_db()
        self.assertFalse(otp.is_used)
        self.assertEqual(otp.attempts, 1)

        # 3. Second attempt with correct OTP
        v2 = OTPVerificationSerializer(data={
            "email": self.user.email,
            "otp_code": real_code,
            "purpose": "forgot_password",
            "reset_token": reset_token,
        })
        self.assertTrue(v2.is_valid(), v2.errors)
        self.assertTrue(bool(v2.validated_data.get("confirm_token")))

        # Verify OTP is now marked as used
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)
        self.assertEqual(otp.attempts, 2)

    @patch("account.services.email_service.EmailService.send_otp_email", return_value=True)
    def test_otp_lockout_after_max_attempts(self, mock_email):
        # Request forgot password OTP
        s = PasswordForgotSerializer(data={"email": self.user.email})
        self.assertTrue(s.is_valid(), s.errors)
        reset_token = s.validated_data.get("reset_token")

        otp = OTP.objects.filter(user=self.user, purpose=self.purpose, is_used=False).order_by("-created_at").first()

        # 1st wrong attempt
        v1 = OTPVerificationSerializer(data={
            "email": self.user.email,
            "otp_code": "000000",
            "purpose": "forgot_password",
            "reset_token": reset_token,
        })
        self.assertFalse(v1.is_valid())
        self.assertIn("2 attempts remaining", str(v1.errors["non_field_errors"][0]))

        # 2nd wrong attempt
        v2 = OTPVerificationSerializer(data={
            "email": self.user.email,
            "otp_code": "000000",
            "purpose": "forgot_password",
            "reset_token": reset_token,
        })
        self.assertFalse(v2.is_valid())
        self.assertIn("1 attempt remaining", str(v2.errors["non_field_errors"][0]))

        # 3rd wrong attempt -> Lockout
        v3 = OTPVerificationSerializer(data={
            "email": self.user.email,
            "otp_code": "000000",
            "purpose": "forgot_password",
            "reset_token": reset_token,
        })
        self.assertFalse(v3.is_valid())
        self.assertIn("Maximum verification attempts exceeded", str(v3.errors["non_field_errors"][0]))

        otp.refresh_from_db()
        self.assertTrue(otp.is_used)
        self.assertEqual(otp.attempts, 3)


class PasswordResetReplayProtectionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="replay_test@example.com",
            password="InitialPassword123!",
            first_name="Replay",
            last_name="Test"
        )
        self.purpose, _ = OTPPurpose.objects.get_or_create(
            slug="forgot_password",
            defaults={
                "name": "Forgot Password",
                "description": "Password reset OTP",
                "expiry_seconds": 900,
                "max_attempts": 3,
                "resend_cooldown_seconds": 60,
                "is_active": True,
            }
        )

    @patch("account.models.otp.OTP.generate_code", return_value="123456")
    @patch("account.services.email_service.EmailService.send_otp_email", return_value=True)
    def test_reset_token_cannot_be_reused_after_otp_verification(self, mock_email, mock_code):
        # 1. Request forgot password
        s = PasswordForgotSerializer(data={"email": self.user.email})
        self.assertTrue(s.is_valid())
        reset_token = s.validated_data["reset_token"]

        # 2. Verify OTP once
        v1 = OTPVerificationSerializer(data={
            "email": self.user.email,
            "otp_code": "123456",
            "purpose": "forgot_password",
            "reset_token": reset_token,
        })
        self.assertTrue(v1.is_valid(), v1.errors)
        confirm_token = v1.validated_data["confirm_token"]
        self.assertTrue(bool(confirm_token))

        # 3. Attempt to use the same reset_token again (Replay attack on reset_token)
        v2 = OTPVerificationSerializer(data={
            "email": self.user.email,
            "otp_code": "123456",
            "purpose": "forgot_password",
            "reset_token": reset_token,
        })
        self.assertFalse(v2.is_valid())
        err = str(v2.errors["non_field_errors"][0])
        self.assertIn("Invalid or expired token", err)

    @patch("account.models.otp.OTP.generate_code", return_value="123456")
    @patch("account.services.email_service.EmailService.send_otp_email", return_value=True)
    def test_confirm_token_cannot_be_reused_after_password_reset(self, mock_email, mock_code):
        # 1. Request forgot password and verify OTP
        s = PasswordForgotSerializer(data={"email": self.user.email})
        self.assertTrue(s.is_valid())
        reset_token = s.validated_data["reset_token"]

        v = OTPVerificationSerializer(data={
            "email": self.user.email,
            "otp_code": "123456",
            "purpose": "forgot_password",
            "reset_token": reset_token,
        })
        self.assertTrue(v.is_valid(), v.errors)
        confirm_token = v.validated_data["confirm_token"]

        # 2. Reset password using confirm_token
        r1 = PasswordResetSerializer(data={
            "email": self.user.email,
            "confirm_token": confirm_token,
            "password": "NewSecretPassword123!",
            "password2": "NewSecretPassword123!",
        })
        self.assertTrue(r1.is_valid(), r1.errors)
        r1.save()

        # Check password actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecretPassword123!"))

        # 3. Replay attack: attempt to use the same confirm_token again
        r2 = PasswordResetSerializer(data={
            "email": self.user.email,
            "confirm_token": confirm_token,
            "password": "AttackerPassword123!",
            "password2": "AttackerPassword123!",
        })
        self.assertFalse(r2.is_valid())
        err = str(r2.errors["non_field_errors"][0])
        self.assertIn("Invalid or expired token", err)

        # Confirm password remains unchanged by the replayed attempt
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("AttackerPassword123!"))
        self.assertTrue(self.user.check_password("NewSecretPassword123!"))


class EmailVerificationAndLoginTestCase(TestCase):
    def setUp(self):
        # Create necessary statuses and roles
        self.pending_status, _ = UserStatus.objects.get_or_create(
            slug="pending",
            defaults={"name": "Pending", "description": "Pending activation", "is_active": True}
        )
        self.active_status, _ = UserStatus.objects.get_or_create(
            slug="active",
            defaults={"name": "Active", "description": "Active account", "is_active": True}
        )
        self.user_role, _ = Role.objects.get_or_create(
            slug="user",
            defaults={"name": "User", "description": "Standard user", "is_active": True}
        )
        self.purpose, _ = OTPPurpose.objects.get_or_create(
            slug="email_verification",
            defaults={
                "name": "Email Verification",
                "description": "Email verification OTP",
                "expiry_seconds": 900,
                "max_attempts": 3,
                "resend_cooldown_seconds": 60,
                "is_active": True,
            }
        )

    @patch("account.models.otp.OTP.generate_code", return_value="987654")
    @patch("account.services.email_service.EmailService.send_otp_email", return_value=True)
    def test_unverified_user_cannot_login_until_email_verified(self, mock_email, mock_code):
        # 1. Register a new user
        reg_serializer = UserRegistrationSerializer(data={
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "tc": True,
        })
        self.assertTrue(reg_serializer.is_valid(), reg_serializer.errors)
        result = reg_serializer.save()
        self.assertEqual(result["status"], "pending")
        self.assertFalse(result["email_verified"])

        # 2. Attempt login BEFORE email verification -> MUST FAIL
        login_before = UserLoginSerializer(data={
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
        })
        self.assertFalse(login_before.is_valid())
        self.assertIn("non_field_errors", login_before.errors)
        err = str(login_before.errors["non_field_errors"][0])
        self.assertIn("Please verify your email", err)

        # 3. Verify email with OTP
        v = OTPVerificationSerializer(data={
            "email": "newuser@example.com",
            "otp_code": "987654",
            "purpose": "email_verification",
        })
        self.assertTrue(v.is_valid(), v.errors)
        
        # In OTPVerificationView, on email_verification, it marks user verified and active
        user = v.validated_user
        user.email_verified = True
        user.status = self.active_status
        user.save()

        # 4. Attempt login AFTER email verification -> MUST SUCCEED
        login_after = UserLoginSerializer(data={
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
        })
        self.assertTrue(login_after.is_valid(), login_after.errors)
        self.assertEqual(login_after.validated_user.email, "newuser@example.com")


class TokenRefreshTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="token_user@example.com",
            password="StrongPassword123!",
            first_name="Token",
            last_name="User"
        )

    def test_refresh_token_rotation_succeeds(self):
        from account.services.jwt_service import JWTService
        from rest_framework_simplejwt.settings import api_settings

        # Generate tokens
        tokens = JWTService.generate_tokens(self.user)
        old_refresh = tokens["refresh"]
        self.assertTrue(bool(old_refresh))

        # Rotate tokens with ROTATE_REFRESH_TOKENS=True
        with patch.object(api_settings, "ROTATE_REFRESH_TOKENS", True):
            result = JWTService.refresh_tokens(old_refresh)
            self.assertTrue(result["success"], result.get("error"))
            self.assertIn("access", result)
            self.assertIn("refresh", result)
            self.assertNotEqual(result["refresh"], old_refresh)


class AdminRBACPermissionsTestCase(TestCase):
    def setUp(self):
        from account.models import Role, UserRole, Permission, RolePermission

        self.admin_role, _ = Role.objects.get_or_create(
            slug="admin",
            defaults={"name": "Admin", "description": "Administrator", "is_active": True}
        )
        self.user = User.objects.create_user(
            email="admin_test@example.com",
            password="AdminPassword123!",
            first_name="Admin",
            last_name="Test"
        )
        UserRole.objects.create(user=self.user, role=self.admin_role)

    def test_admin_has_seeded_rbac_permissions(self):
        from account.services.permission_service import PermissionService
        from account.views.user_crud import check_permission

        # Check permission check for user.list and user.view
        err = check_permission(self.user, "user.list")
        self.assertIsNone(err, "admin should have user.list permission")

        err = check_permission(self.user, "user.view")
        self.assertIsNone(err, "admin should have user.view permission")

        err = check_permission(self.user, "user.edit")
        self.assertIsNone(err, "admin should have user.edit permission")

        # Test synonym fallback: user with only user.read can access user.list
        limited_role, _ = Role.objects.get_or_create(
            slug="auditor",
            defaults={"name": "Auditor", "description": "Read only auditor", "is_active": True}
        )
        read_perm, _ = Permission.objects.get_or_create(
            slug="user.read",
            defaults={"name": "Read User", "module": "user", "is_active": True}
        )
        RolePermission.objects.get_or_create(role=limited_role, permission=read_perm)

        auditor = User.objects.create_user(
            email="auditor@example.com",
            password="AuditorPassword123!",
            first_name="Audit",
            last_name="User"
        )
        UserRole.objects.create(user=auditor, role=limited_role)

        auditor_err = check_permission(auditor, "user.list")
        self.assertIsNone(auditor_err, "user with user.read should access user.list via synonym")


class SocialAuthTestCase(TestCase):
    def setUp(self):
        from account.models import SocialProvider
        self.google_provider, _ = SocialProvider.objects.get_or_create(
            slug="google",
            defaults={"name": "Google", "description": "Google OAuth", "is_active": True}
        )
        self.github_provider, _ = SocialProvider.objects.get_or_create(
            slug="github",
            defaults={"name": "GitHub", "description": "GitHub OAuth", "is_active": True}
        )

    def test_social_auth_google_creates_user_and_returns_tokens(self):
        from account.services.social_auth_service import SocialAuthService
        from account.models import User, SocialAccount

        mock_token_info = {
            "sub": "google-uid-12345",
            "email": "google_user@example.com",
            "given_name": "Google",
            "family_name": "Tester",
            "picture": "https://example.com/photo.jpg",
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_token_info

            result = SocialAuthService.authenticate_google("dummy-id-token")

            self.assertTrue(result["success"], result.get("error"))
            self.assertIn("tokens", result)
            self.assertIn("user", result)
            self.assertTrue(result.get("is_new_user"))

            # Check User and SocialAccount created
            user = User.objects.get(email="google_user@example.com")
            self.assertTrue(user.email_verified)
            self.assertEqual(user.first_name, "Google")
            self.assertEqual(user.last_name, "Tester")

            social_acc = SocialAccount.objects.get(user=user, provider=self.google_provider)
            self.assertEqual(social_acc.provider_user_id, "google-uid-12345")

    def test_social_auth_view_endpoint(self):
        from rest_framework.test import APIClient
        client = APIClient()

        mock_token_info = {
            "sub": "google-uid-67890",
            "email": "api_google@example.com",
            "given_name": "Api",
            "family_name": "Google",
            "picture": "https://example.com/api.jpg",
        }

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_token_info

            resp = client.post(
                "/api/v1/auth/social/login/",
                {"provider": "google", "token": "valid-token"},
                format="json"
            )
            self.assertEqual(resp.status_code, 200, resp.data)
            self.assertIn("data", resp.data)
            self.assertTrue(resp.data["data"]["success"])
            self.assertIn("tokens", resp.data["data"])


class UserProfileAndSocialLinkTestCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="profile_test@example.com",
            password="StrongPassword123!",
            first_name="Profile",
            last_name="Test"
        )
        self.client.force_authenticate(user=self.user)

    def test_user_profile_id_uses_prf_prefix(self):
        from account.models.user_profile import UserProfile
        profile = UserProfile.objects.create(user=self.user)
        self.assertTrue(profile.profile_id.startswith("prf_"), f"profile_id {profile.profile_id} should start with prf_")

    def test_missing_profile_auto_created_without_500(self):
        from account.models.user_profile import UserProfile
        # Ensure user has no profile
        UserProfile.objects.filter(user=self.user).delete()

        # Call profile endpoint
        resp = self.client.get("/api/v1/profile/social-links/")
        self.assertEqual(resp.status_code, 200, resp.data)

        # Call me endpoint
        resp_me = self.client.get("/api/v1/me/")
        self.assertEqual(resp_me.status_code, 200, resp_me.data)

    def test_nonexistent_social_link_returns_404_not_500(self):
        # Update non-existent link
        resp_put = self.client.put(
            "/api/v1/profile/social-links/non-existent-id/",
            {"platform_name": "Twitter", "url": "https://twitter.com/test"},
            format="json"
        )
        self.assertEqual(resp_put.status_code, 404, resp_put.data)

        # Delete non-existent link via direct DELETE and via /delete/
        resp_del1 = self.client.delete("/api/v1/profile/social-links/non-existent-id/")
        self.assertEqual(resp_del1.status_code, 404, resp_del1.data)

        resp_del2 = self.client.delete("/api/v1/profile/social-links/non-existent-id/delete/")
        self.assertEqual(resp_del2.status_code, 404, resp_del2.data)


class UserChangePasswordTestCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="changepass@example.com",
            password="OriginalPassword123!",
            first_name="Change",
            last_name="Pass"
        )
        self.client.force_authenticate(user=self.user)

    def test_password_not_mutated_on_validate_only_on_save(self):
        from account.serializers.user import UserChangePasswordSerializer

        serializer = UserChangePasswordSerializer(
            data={
                "old_password": "OriginalPassword123!",
                "password": "NewChangedPassword123!",
                "password2": "NewChangedPassword123!",
            },
            context={"user": self.user}
        )

        # Validation should succeed
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Before save() is called, database password MUST NOT be changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OriginalPassword123!"))
        self.assertFalse(self.user.check_password("NewChangedPassword123!"))

        # Now call save() -> database password MUST be changed
        serializer.save()
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("OriginalPassword123!"))
        self.assertTrue(self.user.check_password("NewChangedPassword123!"))


class ErrorRendererTestCase(TestCase):
    def test_renderer_unwraps_nested_errors_object(self):
        import json
        from account.renderers import UserRenderer as AccountUserRenderer
        from life_hub.renderers import UserRenderer as LifeHubUserRenderer

        for RendererCls in [AccountUserRenderer, LifeHubUserRenderer]:
            renderer = RendererCls()
            class MockResponse:
                status_code = 400

            context = {"response": MockResponse()}

            # Test 1: Views returning {"errors": serializer.errors}
            data = {"errors": {"email": ["Email already exists."]}}
            rendered = json.loads(renderer.render(data, renderer_context=context))
            self.assertFalse(rendered["success"])
            self.assertEqual(rendered["statusCode"], 400)
            self.assertIn("field_errors", rendered["errors"])
            # Must NOT be double-nested under field_errors["errors"]
            self.assertNotIn("errors", rendered["errors"]["field_errors"])
            self.assertEqual(rendered["errors"]["field_errors"]["email"], ["Email already exists."])

            # Test 2: Views returning string error
            data_str = {"errors": "Invalid OTP code"}
            rendered_str = json.loads(renderer.render(data_str, renderer_context=context))
            self.assertIn("Invalid OTP code", rendered_str["errors"]["non_field_errors"])

            # Test 3: DRF detail error
            data_detail = {"detail": "Authentication credentials were not provided."}
            rendered_detail = json.loads(renderer.render(data_detail, renderer_context=context))
            self.assertEqual(rendered_detail["message"], "Authentication credentials were not provided.")
            self.assertIn("Authentication credentials were not provided.", rendered_detail["errors"]["non_field_errors"])


class OTPResendResetTokenTestCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="resend_test@example.com",
            password="StrongPassword123!",
            first_name="Resend",
            last_name="Tester"
        )
        self.purpose_fp, _ = OTPPurpose.objects.get_or_create(
            slug="forgot_password",
            defaults={"name": "Forgot Password", "code_length": 6, "expiry_minutes": 10, "max_attempts": 3, "cooldown_seconds": 60}
        )
        self.purpose_ev, _ = OTPPurpose.objects.get_or_create(
            slug="email_verification",
            defaults={"name": "Email Verification", "code_length": 6, "expiry_minutes": 10, "max_attempts": 3, "cooldown_seconds": 60}
        )

    @patch("account.models.otp.OTP.generate_code", return_value="654321")
    @patch("account.services.email_service.EmailService.send_otp_email", return_value=True)
    def test_resend_otp_forgot_password_issues_reset_token_and_verifies(self, mock_email, mock_code):
        import json
        from account.models import OTP

        # 1. Call OTP Resend for forgot_password
        response = self.client.post("/api/v1/auth/resend-otp/", {
            "email": "resend_test@example.com",
            "purpose": "forgot_password"
        }, format="json")

        self.assertEqual(response.status_code, 200)
        res_data = json.loads(response.content.decode("utf-8"))
        self.assertTrue(res_data["success"])
        self.assertIsNotNone(res_data["data"])
        self.assertIn("reset_token", res_data["data"])
        reset_token = res_data["data"]["reset_token"]

        # 2. Get the generated OTP
        otp_obj = OTP.objects.filter(
            user=self.user,
            purpose=self.purpose_fp
        ).order_by("-created_at").first()
        self.assertIsNotNone(otp_obj)

        # 3. Verify OTP using the renewed reset_token and generated code
        verify_response = self.client.post("/api/v1/auth/verify-otp/", {
            "email": "resend_test@example.com",
            "otp_code": "654321",
            "purpose": "forgot_password",
            "reset_token": reset_token
        }, format="json")

        self.assertEqual(verify_response.status_code, 200)
        verify_data = json.loads(verify_response.content.decode("utf-8"))
        self.assertTrue(verify_data["success"])
        self.assertIn("confirm_token", verify_data["data"])

    def test_resend_otp_email_verification_does_not_issue_reset_token(self):
        import json

        response = self.client.post("/api/v1/auth/resend-otp/", {
            "email": "resend_test@example.com",
            "purpose": "email_verification"
        }, format="json")

        self.assertEqual(response.status_code, 200)
        res_data = json.loads(response.content.decode("utf-8"))
        self.assertTrue(res_data["success"])
        self.assertNotIn("reset_token", res_data.get("data") or {})


class ForgotPasswordEmailVerificationTestCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.pending_status, _ = UserStatus.objects.get_or_create(
            slug="pending",
            defaults={"name": "Pending", "is_active": True}
        )
        self.active_status, _ = UserStatus.objects.get_or_create(
            slug="active",
            defaults={"name": "Active", "is_active": True}
        )
        self.role_user, _ = Role.objects.get_or_create(
            slug="user",
            defaults={"name": "User", "is_active": True}
        )
        self.user = User.objects.create_user(
            email="forgot_verify@example.com",
            password="OldPassword123!",
            first_name="Forgot",
            last_name="Verify",
        )
        self.user.email_verified = False
        self.user.status = self.pending_status
        self.user.save(update_fields=["email_verified", "status"])

        self.purpose_fp, _ = OTPPurpose.objects.get_or_create(
            slug="forgot_password",
            defaults={"name": "Forgot Password", "code_length": 6, "expiry_minutes": 10, "max_attempts": 3, "cooldown_seconds": 60}
        )

    @patch("account.models.otp.OTP.generate_code", return_value="123456")
    @patch("account.services.email_service.EmailService.send_otp_email", return_value=True)
    def test_unverified_user_can_login_after_forgot_password_reset(self, mock_email, mock_code):
        import json

        # 1. User tries to log in with old password -> should fail due to unverified email
        login_res1 = self.client.post("/api/v1/auth/login/", {
            "email": "forgot_verify@example.com",
            "password": "OldPassword123!",
        }, format="json")
        self.assertEqual(login_res1.status_code, 400)
        login_data1 = json.loads(login_res1.content.decode("utf-8"))
        self.assertIn("Please verify your email", str(login_data1["errors"]["non_field_errors"]))

        # 2. User requests forgot password OTP
        fp_res = self.client.post("/api/v1/auth/forgot-password/", {
            "email": "forgot_verify@example.com",
        }, format="json")
        self.assertEqual(fp_res.status_code, 200)
        fp_data = json.loads(fp_res.content.decode("utf-8"))
        reset_token = fp_data["data"]["reset_token"]

        # 3. User verifies OTP sent to their email
        verify_res = self.client.post("/api/v1/auth/verify-otp/", {
            "email": "forgot_verify@example.com",
            "otp_code": "123456",
            "purpose": "forgot_password",
            "reset_token": reset_token,
        }, format="json")
        self.assertEqual(verify_res.status_code, 200)
        verify_data = json.loads(verify_res.content.decode("utf-8"))
        confirm_token = verify_data["data"]["confirm_token"]

        # User's email should now be verified and status active
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        self.assertEqual(self.user.status.slug, "active")

        # 4. User resets password
        reset_res = self.client.post("/api/v1/auth/reset-password/", {
            "email": "forgot_verify@example.com",
            "confirm_token": confirm_token,
            "password": "NewSecretPassword123!",
            "password2": "NewSecretPassword123!",
        }, format="json")
        self.assertEqual(reset_res.status_code, 200)

        # 5. User logs in with newly reset password -> MUST succeed!
        login_res2 = self.client.post("/api/v1/auth/login/", {
            "email": "forgot_verify@example.com",
            "password": "NewSecretPassword123!",
        }, format="json")
        self.assertEqual(login_res2.status_code, 200)
        login_data2 = json.loads(login_res2.content.decode("utf-8"))
        self.assertTrue(login_data2["success"])
        self.assertIn("tokens", login_data2["data"])
        self.assertTrue(login_data2["data"]["user"]["email_verified"])


class RoleAccessControlTestCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()

        self.active_status, _ = UserStatus.objects.get_or_create(
            slug="active",
            defaults={"name": "Active", "is_active": True}
        )
        self.role_user, _ = Role.objects.get_or_create(
            slug="user",
            defaults={"name": "User", "is_active": True}
        )
        self.role_admin, _ = Role.objects.get_or_create(
            slug="admin",
            defaults={"name": "Admin", "is_active": True}
        )

        # Standard non-admin user
        self.normal_user = User.objects.create_user(
            email="regular_user@example.com",
            password="UserPass123!",
            first_name="Regular",
            last_name="User",
        )
        self.normal_user.email_verified = True
        self.normal_user.status = self.active_status
        self.normal_user.is_superuser = False
        self.normal_user.save()
        UserRole.objects.get_or_create(user=self.normal_user, role=self.role_user)

        # Admin user
        self.admin_user = User.objects.create_user(
            email="admin_user@example.com",
            password="AdminPass123!",
            first_name="Admin",
            last_name="User",
        )
        self.admin_user.email_verified = True
        self.admin_user.status = self.active_status
        self.admin_user.is_superuser = True
        self.admin_user.save()
        UserRole.objects.get_or_create(user=self.admin_user, role=self.role_admin)

    def test_normal_user_denied_access_to_user_list_api(self):
        import json
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.get("/api/v1/accounts/users/")
        self.assertEqual(res.status_code, 403)
        data = json.loads(res.content.decode("utf-8"))
        self.assertIn("You do not have permission to perform this action.", str(data["errors"]["non_field_errors"]))

    def test_admin_user_granted_access_to_user_list_api(self):
        import json
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get("/api/v1/accounts/users/")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode("utf-8"))
        self.assertTrue(data["success"])
        self.assertIn("results", data["data"])
        self.assertEqual(data["data"]["count"], 2)

    def test_login_response_contains_role_and_superuser_flags(self):
        import json
        # Normal user login
        res = self.client.post("/api/v1/auth/login/", {
            "email": "regular_user@example.com",
            "password": "UserPass123!",
        }, format="json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode("utf-8"))
        user_info = data["data"]["user"]
        self.assertEqual(user_info["role"], "user")
        self.assertIn("user", user_info["roles"])
        self.assertFalse(user_info["is_superuser"])

        # Admin user login
        res_admin = self.client.post("/api/v1/auth/login/", {
            "email": "admin_user@example.com",
            "password": "AdminPass123!",
        }, format="json")
        self.assertEqual(res_admin.status_code, 200)
        admin_data = json.loads(res_admin.content.decode("utf-8"))
        admin_info = admin_data["data"]["user"]
        self.assertEqual(admin_info["role"], "admin")
        self.assertIn("admin", admin_info["roles"])
        self.assertTrue(admin_info["is_superuser"])

    def test_user_me_endpoint_contains_role_and_superuser_flags(self):
        import json
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.get("/api/v1/me/")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode("utf-8"))
        user_info = data["data"]["user"]
        self.assertEqual(user_info["role"], "user")
        self.assertIn("user", user_info["roles"])
        self.assertFalse(user_info["is_superuser"])


class AdminUserActivationAndLoginTestCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()

        self.pending_status, _ = UserStatus.objects.get_or_create(
            slug="pending",
            defaults={"name": "Pending", "is_active": True}
        )
        self.active_status, _ = UserStatus.objects.get_or_create(
            slug="active",
            defaults={"name": "Active", "is_active": True}
        )
        self.blocked_status, _ = UserStatus.objects.get_or_create(
            slug="blocked",
            defaults={"name": "Blocked", "is_active": True}
        )
        self.role_admin, _ = Role.objects.get_or_create(
            slug="admin",
            defaults={"name": "Admin", "is_active": True}
        )
        self.role_user, _ = Role.objects.get_or_create(
            slug="user",
            defaults={"name": "User", "is_active": True}
        )

        # Admin user
        self.admin = User.objects.create_user(
            email="admin_activator@example.com",
            password="AdminPassword123!",
            first_name="Admin",
            last_name="Activator",
        )
        self.admin.email_verified = True
        self.admin.status = self.active_status
        self.admin.is_superuser = True
        self.admin.save()
        UserRole.objects.get_or_create(user=self.admin, role=self.role_admin)

    def test_admin_created_user_activation_and_login_flow(self):
        import json
        self.client.force_authenticate(user=self.admin)

        # 1. Admin creates new user via API
        create_res = self.client.post("/api/v1/accounts/users/create/", {
            "email": "newly_created@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!",
            "roles": ["user"],
            "send_email": False,
        }, format="json")
        self.assertEqual(create_res.status_code, 201)
        created_data = json.loads(create_res.content.decode("utf-8"))
        user_id = created_data["data"]["user_id"]

        new_user = User.objects.get(user_id=user_id)
        self.assertEqual(new_user.status.slug, "pending")
        self.assertFalse(new_user.email_verified)

        # 2. User attempts to login while in pending status -> Should fail with email verification prompt
        self.client.logout()
        login_res_pending = self.client.post("/api/v1/auth/login/", {
            "email": "newly_created@example.com",
            "password": "StrongPassword123!",
        }, format="json")
        self.assertEqual(login_res_pending.status_code, 400)
        pending_data = json.loads(login_res_pending.content.decode("utf-8"))
        self.assertIn("Please verify your email", str(pending_data["errors"]["non_field_errors"]))

        # 3. Admin updates status to active
        self.client.force_authenticate(user=self.admin)
        status_update_res = self.client.patch(f"/api/v1/accounts/users/{user_id}/status/", {
            "status_slug": "active",
            "reason": "Admin approved and activated user",
            "send_email": False,
        }, format="json")
        self.assertEqual(status_update_res.status_code, 200)

        new_user.refresh_from_db()
        self.assertEqual(new_user.status.slug, "active")
        self.assertTrue(new_user.email_verified)
        self.assertIsNotNone(new_user.email_verified_at)

        # 4. User logs in with correct credentials now that they are active -> MUST SUCCEED!
        self.client.logout()
        login_res_active = self.client.post("/api/v1/auth/login/", {
            "email": "newly_created@example.com",
            "password": "StrongPassword123!",
        }, format="json")
        self.assertEqual(login_res_active.status_code, 200)
        active_data = json.loads(login_res_active.content.decode("utf-8"))
        self.assertTrue(active_data["success"])
        self.assertIn("tokens", active_data["data"])
        self.assertEqual(active_data["data"]["user"]["status"], "active")
        self.assertTrue(active_data["data"]["user"]["email_verified"])

        # 5. Admin updates status to blocked
        self.client.force_authenticate(user=self.admin)
        block_res = self.client.patch(f"/api/v1/accounts/users/{user_id}/status/", {
            "action": "block",
            "reason": "Policy violation",
            "send_email": False,
        }, format="json")
        self.assertEqual(block_res.status_code, 200)

        # 6. User attempts to login while blocked -> MUST fail with Account is blocked
        self.client.logout()
        login_res_blocked = self.client.post("/api/v1/auth/login/", {
            "email": "newly_created@example.com",
            "password": "StrongPassword123!",
        }, format="json")
        self.assertEqual(login_res_blocked.status_code, 400)
        blocked_data = json.loads(login_res_blocked.content.decode("utf-8"))
        self.assertIn("Account is blocked", str(blocked_data["errors"]["non_field_errors"]))

    @patch("account.models.otp.OTP.generate_code", return_value="654321")
    @patch("account.services.email_service.EmailService.send_otp_email", return_value=True)
    def test_pending_user_verification_otp_flow_and_auto_login(self, mock_email, mock_code):
        import json
        from account.models import OTP

        # 1. Admin creates a user in pending status
        self.client.force_authenticate(user=self.admin)
        create_res = self.client.post("/api/v1/accounts/users/create/", {
            "email": "pending_verify@example.com",
            "first_name": "Pending",
            "last_name": "Verify",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!",
            "roles": ["user"],
            "send_email": False,
        }, format="json")
        self.assertEqual(create_res.status_code, 201)
        created_data = json.loads(create_res.content.decode("utf-8"))
        user_id = created_data["data"]["user_id"]

        user = User.objects.get(user_id=user_id)
        self.assertEqual(user.status.slug, "pending")
        self.assertFalse(user.email_verified)

        # 2. User attempts to login while pending -> must fail with email verification prompt
        self.client.logout()
        login_res_pending = self.client.post("/api/v1/auth/login/", {
            "email": "pending_verify@example.com",
            "password": "StrongPassword123!",
        }, format="json")
        self.assertEqual(login_res_pending.status_code, 400)
        pending_data = json.loads(login_res_pending.content.decode("utf-8"))
        self.assertIn("Please verify your email", str(pending_data["errors"]["non_field_errors"]))

        # 3. User clicks Verify Email, which triggers resend-otp
        resend_res = self.client.post("/api/v1/auth/resend-otp/", {
            "email": "pending_verify@example.com",
            "purpose": "email_verification",
        }, format="json")
        self.assertEqual(resend_res.status_code, 200)
        resend_data = json.loads(resend_res.content.decode("utf-8"))
        self.assertTrue(resend_data["success"])
        self.assertEqual(resend_data["data"]["cooldown_seconds"], 60)

        # 4. User verifies OTP with 654321 -> MUST succeed, activate user, and return tokens + session for auto-login
        verify_res = self.client.post("/api/v1/auth/verify-otp/", {
            "email": "pending_verify@example.com",
            "otp_code": "654321",
            "purpose": "email_verification",
        }, format="json")
        self.assertEqual(verify_res.status_code, 200)
        verify_data = json.loads(verify_res.content.decode("utf-8"))
        self.assertTrue(verify_data["success"])
        self.assertEqual(verify_data["message"], "Email verified successfully")

        # Verify auto-login payload is present
        self.assertIsNotNone(verify_data["data"])
        self.assertIn("tokens", verify_data["data"])
        self.assertIn("access", verify_data["data"]["tokens"])
        self.assertIn("refresh", verify_data["data"]["tokens"])
        self.assertIn("user", verify_data["data"])
        self.assertIn("session", verify_data["data"])

        # Verify user state in DB
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertEqual(user.status.slug, "active")
        self.assertIsNotNone(user.email_verified_at)






