"""Contains attribute node."""

from aisle.parser.nodes.base import Node


class AttrNode(Node):
    """
    Attribute node.

    Example:
        tech = Python, Litestar

    """

    def __init__(
            self,
            line: int,
            name: str,
            value: str,
    ):
        """Create node."""
        super().__init__(line)
        self.name = name
        self.value = value

    def __repr__(self):
        """Convert to string repr."""
        return f"Attr({self.name} = {self.value})"
