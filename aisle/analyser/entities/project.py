from dataclasses import dataclass
from typing import Protocol

from aisle.analyser.entities.styling import LegendStyling


class ProjectEntity(Protocol):
    ...


@dataclass
class Project:
    name: str
    description: str
    namespace: dict[str, ProjectEntity]
    styling: list[LegendStyling]
    comments: list[str]
