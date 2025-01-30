from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING

from aisle.analyser.entities.styling import LegendStyling

if TYPE_CHECKING:  # pragma: no cover
    from aisle.analyser.entities.containers import ServiceEntity
    from aisle.analyser.entities.context import ActorEntity, SystemEntity
    from aisle.analyser.entities.deployment import DeploymentEntity


class ProjectEntity(Protocol):
    name: str


@dataclass
class Project:
    name: str
    description: str
    namespace: dict[str, ProjectEntity]
    styling: list[LegendStyling]
    comments: list[str]

    def get_services_of_system(
            self, system_name: str
    ) -> Collection["ServiceEntity"]:
        from aisle.analyser.entities.containers import ServiceEntity
        return [
            service for service in self.namespace.values()
            if isinstance(service, ServiceEntity)
            and service.system == system_name
        ]

    def get_actors(self) -> Sequence["ActorEntity"]:
        from aisle.analyser.entities.context import ActorEntity
        return [
            entity for entity in self.namespace.values()
            if isinstance(entity, ActorEntity)
        ]

    def get_systems(self) -> Sequence["SystemEntity"]:
        from aisle.analyser.entities.context import SystemEntity
        return [
            entity for entity in self.namespace.values()
            if isinstance(entity, SystemEntity)
        ]

    def get_deployments(self) -> Sequence["DeploymentEntity"]:
        from aisle.analyser.entities.deployment import DeploymentEntity
        return [
            entity for entity in self.namespace.values()
            if isinstance(entity, DeploymentEntity)
        ]
