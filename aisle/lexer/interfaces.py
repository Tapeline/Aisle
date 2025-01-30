from abc import ABC, abstractmethod
from collections.abc import Sequence

from aisle.lexer.tokens import Token


class AbstractLexer(ABC):
    """Tokenizer interface."""

    @abstractmethod
    def __init__(
            self,
            source: str,
            tab_size: int = 4,
    ) -> None:
        """Create tokenizer."""

    @abstractmethod
    def scan(self) -> Sequence[Token]:
        """Get tokens from text."""
