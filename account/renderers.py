from rest_framework import renderers
import json


class UserRenderer(renderers.JSONRenderer):
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get(
            "response") if renderer_context else None
        status_code = getattr(response, "status_code", 200)

        success = 200 <= status_code < 300
        message = None
        errors = None
        formatted_data = None

        if not success:
            # Handle DRF ValidationError or custom error messages
            if isinstance(data, dict):
                message = data.get("message", "Request failed")
                field_errors = {}
                non_field_errors = []

                # Separate field and non-field errors
                for key, value in data.items():
                    if key == "non_field_errors":
                        non_field_errors = value
                    elif key not in ["message", "detail"]:
                        field_errors[key] = value
                    elif key == "detail":
                        non_field_errors = [value]

                errors = {
                    "field_errors": field_errors if field_errors else None,
                    "non_field_errors": non_field_errors or None,
                }
            else:
                message = "Request failed"
                errors = {"non_field_errors": [str(data)]}
        else:
            message = data.get("message", "Request successful")
            formatted_data = data.get("data", data)

        return json.dumps({
            "success": success,
            "statusCode": status_code,
            "message": message,
            "data": formatted_data if success else None,
            "errors": errors if not success else None,
        })