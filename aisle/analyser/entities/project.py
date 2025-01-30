from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from aisle.analyser.entities.styling import LegendStyling

if TYPE_CHECKING:  # pragma: no cover
    from aisle.analyser.entities.containers import ServiceEntity
    from aisle.analyser.entities.context import ActorEntity, SystemEntity
    from aisle.analyser.entities.deployment import DeploymentEntity


class ProjectEntity(Protocol):
    """Base for project entities."""

    name: str


@dataclass
class Project:
    """Represents an Aisle project."""

    name: str
    description: str
    namespace: dict[str, ProjectEntity]
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
