from abc import ABC, abstractmethod
from typing import Callable, Mapping

from aisle.analyser.entities.project import Project


type FileGenerator = Callable[[], str]


class AbstractProjectGenerator(ABC):
    """ABC for project code generators."""

    file_extension: str = ""

    @abstractmethod
    def __init__(self, project: Project) -> None:
        """Create project generator."""

    @property
    @abstractmethod
    def file_generators(self) -> Mapping[str, FileGenerator]:
        """Get generators"""
