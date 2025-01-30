from dataclasses import dataclass

from aisle.analyser.entities.links import Link
from aisle.analyser.entities.project import ProjectEntity


@dataclass
class ServiceEntity(ProjectEntity):
    name: str
    description: str
    system: str | None
    tech: str | None
    links: list[Link]
    tags: list[str]
    is_external: bool = False
