from dataclasses import dataclass

from aisle.parser.nodes.links import LinkType


@dataclass
class Link:
    type: LinkType
    to: str
    over: str | None
    description: str
