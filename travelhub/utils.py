# travelhub/utils.py

import ulid


def generate_ulid_with_prefix(prefix: str) -> str:
    """
    Generates a non-predictable, time-sortable ID
    Example: trv_01HX9Z2Y8J4W7R9F6Q
    """
    return f"{prefix}_{ulid.new()}"
