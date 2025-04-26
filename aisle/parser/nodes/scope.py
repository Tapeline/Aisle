"""Contains classes related to scope node."""

from enum import Enum

from aisle.parser.nodes.base import Node


class ScopeType(Enum):
    """Type of scope."""

    CONTEXT = "context"
    CONTAINERS = "containers"
    DEPLOYMENT = "deployment"
    LEGEND = "legend"


class ScopeNode(Node):
    """
    Represents a scope marker.

    Examples:
        scope context MyApp
        scope legend MyApp
        scope containers MyApp
        scope deployment MyApp

    """

    def __init__(self, line: int, scope_type: ScopeType, scope_name: str):
        """Create node."""
        super().__init__(line)
        self.scope_type = scope_type
        self.scope_name = scope_name

    def __repr__(self) -> str:
        """Convert to string repr."""
        return f"Scope({self.scope_type.value}: {self.scope_name})"
