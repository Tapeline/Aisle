import string
from typing import Final

ALLOWED_CHARS: Final = (
    string.ascii_letters +
    string.digits +
    "_ "
)
