import hashlib

from aisle.codegen.impl.d2.constants import ALLOWED_CHARS


def safe_name(name: str) -> str:
    """Ensure name is safe to use as identifier."""
    filtered_name = "".join(char for char in name if char in ALLOWED_CHARS)
    hash_part = hashlib.md5(name.encode()).hexdigest()[:8]
    if filtered_name == name:
        return filtered_name
    return f"{filtered_name}_{hash_part}"
