from rest_framework import renderers
import json
from datetime import datetime, date
from decimal import Decimal


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime and other non-serializable types"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


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
            field_errors = {}
            non_field_errors = []
            message = "Request failed"

            if isinstance(data, dict):
                # 1. Determine human-readable message
                if "message" in data and data["message"]:
                    message = str(data["message"])
                elif "detail" in data and data["detail"]:
                    message = str(data["detail"])

                # 2. Extract errors source (unwrap if wrapped under 'errors' or 'error')
                raw_errors = data.get("errors")
                if raw_errors is None and "error" in data:
                    raw_errors = data.get("error")

                if isinstance(raw_errors, dict):
                    for k, v in raw_errors.items():
                        if k == "non_field_errors":
                            if isinstance(v, list):
                                non_field_errors.extend(v)
                            else:
                                non_field_errors.append(str(v))
                        else:
                            field_errors[k] = v if isinstance(v, (list, dict)) else [str(v)]
                elif isinstance(raw_errors, list):
                    non_field_errors.extend(raw_errors)
                elif isinstance(raw_errors, str):
                    non_field_errors.append(raw_errors)

                # 3. Process remaining keys at top level of data
                for key, value in data.items():
                    if key in ["message", "errors", "error", "data", "success", "statusCode"]:
                        continue
                    if key == "non_field_errors":
                        if isinstance(value, list):
                            non_field_errors.extend(value)
                        else:
                            non_field_errors.append(str(value))
                    elif key == "detail":
                        non_field_errors.append(str(value))
                    else:
                        field_errors[key] = value if isinstance(value, (list, dict)) else [str(value)]

                # 4. If no specific errors parsed but there is an error message, include in non_field_errors
                if not field_errors and not non_field_errors:
                    if message and message != "Request failed":
                        non_field_errors.append(message)

                if non_field_errors:
                    seen = set()
                    deduped = []
                    for item in non_field_errors:
                        s = str(item)
                        if s not in seen:
                            seen.add(s)
                            deduped.append(item)
                    non_field_errors = deduped

                errors = {
                    "field_errors": field_errors if field_errors else None,
                    "non_field_errors": non_field_errors if non_field_errors else None,
                }
            elif isinstance(data, list):
                errors = {
                    "field_errors": None,
                    "non_field_errors": data,
                }
            else:
                errors = {
                    "field_errors": None,
                    "non_field_errors": [str(data)],
                }
        else:
            if isinstance(data, dict):
                message = data.get("message", "Request successful")
                formatted_data = data.get("data", data)
            else:
                message = "Request successful"
                formatted_data = data

        return json.dumps({
            "success": success,
            "statusCode": status_code,
            "message": message,
            "data": formatted_data if success else None,
            "errors": errors if not success else None,
        }, cls=CustomJSONEncoder)