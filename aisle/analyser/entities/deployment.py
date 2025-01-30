from dataclasses import dataclass

from aisle.analyser.entities.project import ProjectEntity


@dataclass
class ServiceDeployment:
    """Deployment of service."""

    service_name: str
    deploy_as: str


@dataclass
class DeploymentEntity(ProjectEntity):
    """Deployment entity."""

    name: str
    description: str
    deploys: list[ServiceDeployment]
    inner_entities: list["DeploymentEntity"]
    tags: list[str]
    is_external: bool = False
