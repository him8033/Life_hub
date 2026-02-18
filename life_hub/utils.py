# travelhub/utils.py

import ulid


def generate_ulid_with_prefix(prefix: str) -> str:
    """
    Generates a non-predictable, time-sortable ID
    Example: trv_01HX9Z2Y8J4W7R9F6Q
    """
    return f"{prefix}_{ulid.new()}"


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")
