from abc import ABC, abstractmethod
from collections.abc import Sequence

from aisle.analyser.entities.project import Project
from aisle.parser.nodes.base import Node


class AbstractAnalyser(ABC):
    """ABC for analyser."""

    @abstractmethod
    def __init__(self, nodes: Sequence[Node]):
        """Create analyser."""

    @abstractmethod
    def analyse(self) -> Project:
        """Analyse AST and create project."""
