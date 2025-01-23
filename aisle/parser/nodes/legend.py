"""Contains nodes related to legend."""

from collections.abc import Sequence
from enum import Enum

from attrs import frozen

from aisle.parser.nodes.base import Node


class LegendSelectorType(Enum):
    """Type of selector."""

    CONTAINS_REGEX = "contains"
    HAS_TAG = "tag"
    MATCHES_REGEX = "="
    ENTITY_TYPE = "entity"


@frozen
class LegendSelector:
    """Styling selector."""

    type: LegendSelectorType
    selector: str


class LegendDeclarationNode(Node):
    """
    Represents a legend styling rule.

    Example:
        [tag Docker]:
            bg = #1D63ED

    """

    def __init__(
            self,
            line: int,
            selector: LegendSelector,
            body: Sequence[Node],
    ):
        """Create node."""
        super().__init__(line)
        self.selector = selector
        self.body = body

    def __repr__(self):
        """Convert to string repr."""
        return f"Legend({self.selector}: {'; '.join(map(str, self.body))})"
