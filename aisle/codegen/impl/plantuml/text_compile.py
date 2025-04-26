import hashlib

from aisle.analyser.entities.containers import ServiceEntity
from aisle.analyser.entities.context import SystemEntity
from aisle.analyser.entities.styling import StylingAttributes
from aisle.codegen.impl.plantuml.constants import (
    ALLOWED_CHARS,
    STYLING_ATTR_MAP,
    TAGS_FOR_DB,
    TAGS_FOR_QUEUE,
)


def safe_name(name: str) -> str:
    """Ensure name is safe to use as identifier."""
    name = name.replace(" ", "_")
    filtered_name = "".join(char for char in name if char in ALLOWED_CHARS)
    hash_part = hashlib.md5(name.encode()).hexdigest()[:8]
    if filtered_name == name:
        return filtered_name
    return f"{filtered_name}_{hash_part}"


def compile_tags(tags: list[str]) -> str:
    """Join all tags with +."""
    return "+".join(map(safe_name, tags))


def safe_str(text: str | None) -> str:
    r"""Get rid of unsafe string chars like " or \n."""
    if text is None:
        return ""
    return text.replace('"', r'\"').replace("\n", r"\n")


def get_node_type(
        base_type: str,
        service: ServiceEntity | SystemEntity
) -> str:
    """Get node type."""
    if any(tag in TAGS_FOR_DB for tag in service.tags):
        return f"{base_type}Db"
    if any(tag in TAGS_FOR_QUEUE for tag in service.tags):
        return f"{base_type}Queue"
    return base_type


def gen_styling_attrs(attrs: StylingAttributes) -> str:
    """Gen styling string."""
    attrs_dict = {
        puml_key: repr(getattr(attrs, aisle_key))
        for aisle_key, puml_key in STYLING_ATTR_MAP.items()
        if getattr(attrs, aisle_key, None)
    }
    return ", ".join(
        f"${puml_key}={attr_value}"
        for puml_key, attr_value in attrs_dict.items()
    )
