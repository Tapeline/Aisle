import string
from types import MappingProxyType
from typing import Final

STYLING_ATTR_MAP: Final = MappingProxyType({
    "bg": "backgroundColor",
    "fg": "foregroundColor",
    "border_color": "borderColor"
})

TAGS_FOR_DB: Final = (
    "db", "database",
)
TAGS_FOR_QUEUE: Final = (
    "queue",
)

ALLOWED_CHARS: Final = (
    string.ascii_letters +
    string.digits +
    "_"
)
