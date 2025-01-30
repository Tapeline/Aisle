from dataclasses import dataclass

from aisle.parser.nodes.links import LinkType


@dataclass
class Link:
    """Link between entities."""

    type: LinkType
    to: str
    over: str | None
    description: str
