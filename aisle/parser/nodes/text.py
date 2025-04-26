"""Text node."""

from aisle.parser.nodes.base import Node


class TextNode(Node):
    """Represents a textual description or a comment."""

    def __init__(self, line: int, text: str) -> None:
        """Create node."""
        super().__init__(line)
        self.text = text

    def __repr__(self) -> str:
        """Convert to string repr."""
        return f"Text({self.text})"
