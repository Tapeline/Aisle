from collections.abc import Collection, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from aisle.analyser.entities.styling import LegendStyling
from aisle.exceptions import AisleError

if TYPE_CHECKING:  # pragma: no cover
    from aisle.analyser.entities.containers import ServiceEntity
    from aisle.analyser.entities.context import ActorEntity, SystemEntity
    from aisle.analyser.entities.deployment import DeploymentEntity


class ProjectEntity(Protocol):
    """Base for project entities."""

    name: str


class NameNotFoundError(AisleError):
    """Raised when a name is not found."""

    def __init__(self, name: str) -> None:
        """Create exception and set name."""
        self.name = name


@dataclass
class Namespace:
    """Project namespace."""

    _ns: dict[str, ProjectEntity] = field(default_factory=dict)

    def __setitem__(self, key: str, value: ProjectEntity) -> None:
        """Set name."""
        self._ns[key] = value

    def __getitem__(self, key: str) -> ProjectEntity:
        """Get a name or raise custom exception."""
        if key not in self._ns:
            raise NameNotFoundError(key)
        return self._ns[key]

    def values(self) -> Collection[ProjectEntity]:  # noqa: WPS110
        """Like dict::values."""
        return self._ns.values()


@dataclass
class Project:
    """Represents an Aisle project."""

    name: str
    description: str
    namespace: Namespace
    styling: list[LegendStyling]
    comments: list[str]

    def get_services_of_system(
            self, system_name: str
    ) -> Collection["ServiceEntity"]:
        """Get all services inside given system."""
        from aisle.analyser.entities.containers import ServiceEntity
        return [
            service for service in self.namespace.values()
            if (
                isinstance(service, ServiceEntity) and
                service.system == system_name
            )
        ]

    def get_actors(self) -> Sequence["ActorEntity"]:
        """Get all actor entities."""
        from aisle.analyser.entities.context import ActorEntity
        return [
            entity for entity in self.namespace.values()
            if isinstance(entity, ActorEntity)
        ]

    def get_systems(self) -> Sequence["SystemEntity"]:
        """Get all system entities."""
        from aisle.analyser.entities.context import SystemEntity
        return [
            entity for entity in self.namespace.values()
            if isinstance(entity, SystemEntity)
        ]

    def get_deployments(self) -> Sequence["DeploymentEntity"]:
        """Get all deployment entities."""
        from aisle.analyser.entities.deployment import DeploymentEntity
        return [
            entity for entity in self.namespace.values()
            if isinstance(entity, DeploymentEntity)
        ]
