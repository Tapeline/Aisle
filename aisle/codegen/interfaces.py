from abc import ABC, abstractmethod

from aisle.analyser.entities.project import Project


class AbstractProjectGenerator(ABC):
    """ABC for project code generators."""

    file_extension: str = ""

    @abstractmethod
    def __init__(self, project: Project) -> None:
        """Create project generator."""

    @abstractmethod
    def generate_context(self) -> str:
        """Generate context code."""

    @abstractmethod
    def generate_containers(self) -> str:
        """Generate containers code."""

    @abstractmethod
    def generate_deployments(self) -> str:
        """Generate deployments code."""
