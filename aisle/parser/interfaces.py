from abc import ABC, abstractmethod
from collections.abc import Sequence

from aisle.lexer.tokens import Token
from aisle.parser.nodes.base import Node


class AbstractParser(ABC):
    """ABC for parsers."""

    @abstractmethod
    def __init__(self, source_code: str, tokens: Sequence[Token]):
        """Create parser."""

    @abstractmethod
    def parse(self) -> Sequence[Node]:
        """Get AST from tokens."""
