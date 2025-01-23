"""Basic definitions."""


class Node:
    """Base for all nodes."""

    def __init__(self, line: int):
        """Create node."""
        self.line = line
