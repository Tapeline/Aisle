import textwrap


def indent(text: str, indent_level: int) -> str:
    """Indent by n spaces."""
    return textwrap.indent(text, prefix=" " * indent_level)
