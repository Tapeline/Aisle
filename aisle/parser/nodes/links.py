"""Contains classes related to link node."""

import enum
from collections.abc import Sequence

from aisle.parser.nodes.base import Node


class LinkType(enum.Enum):
    """Type of link."""

    OUTGOING = "-->"
    INCOMING = "<--"
    BIDIRECTIONAL = "<->"
    NON_DIRECTED = "---"


class LinkNode(Node):
    """
    Represents a single link.

    Examples:
        <-- MyBackend

        <-> MyBackend over HTTP

        --> MyMetricsMicroservice over gRPC:
            Sends metrics

    """

    def __init__(
            self,
            line: int,
            link_type: LinkType,
            link_to: str,
            link_over: str | None = None,
            link_description: Sequence[str] | None = None,
    ):
        """Create node."""
        super().__init__(line)
        if link_description is None:
            link_description = []
        self.type = link_type
        self.to = link_to
        self.over = link_over
        self.description = link_description

    def __repr__(self):
        """Convert to string repr."""
        return (
            f"Link({self.type.value} {self.to} "
            f"{self.over} {self.description})"
        )


class LinkCollectionNode(Node):
    """
    Represents a collection of links.

    Example:
        links:
            --> Service1
            --> Service2
        etc.

    """

    def __init__(self, line: int, links: Sequence[LinkNode]):
        """Create node."""
        super().__init__(line)
        self.links = links

    def __repr__(self):
        """Convert to string repr."""
        return f"Links[{'; '.join(map(str, self.links))}]"
