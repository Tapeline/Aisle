"""Contains different entity nodes."""

from collections.abc import Sequence
from enum import Enum

from aisle.parser.nodes.base import Node


class EntityType(Enum):
    """Type of entity."""

    SYSTEM = "system"
    SERVICE = "service"
    DEPLOYMENT = "deployment"
    ACTOR = "actor"


class EntityNode(Node):
    """
    Represents an entity.

    Examples:
        service MyService:
            ...

        deployment MyDeployment:
            ...

        etc.

    """

    def __init__(
            self,
            line: int,
            entity_type: EntityType,
            name: str,
            tags: Sequence[str],
            body: Sequence[Node],
            *,
            is_external: bool = False,
    ):
        """Create node."""
        super().__init__(line)
        self.type = entity_type
        self.body = body
        self.name = name
        self.tags = tags
        self.is_external = is_external

    def __repr__(self):
        """Convert to string repr."""
        ext = "external " if self.is_external else ""
        return (
            f"Entity({ext}{self.type.value} {self.name} {self.tags}: "
            f"{'; '.join(map(str, self.body))})"
        )


class ProjectDefNode(Node):
    """
    Represents a project definition.

    Example:
        scope project MyProject:
            My project description.

    """

    def __init__(
            self,
            line: int,
            name: str,
            description: Sequence[str],
    ):
        """Create node."""
        super().__init__(line)
        self.name = name
        self.description = description

    def __repr__(self):
        """Convert to string repr."""
        return f"Project({self.name}: {self.description})"


class DeployNode(Node):
    """
    Declaration or deployment.

    Example:
        deploy MyService = Docker Container

    """

    def __init__(
            self,
            line: int,
            target: str,
            deploy_as: str | None,
    ):
        """Create node."""
        super().__init__(line)
        self.target = target
        self.deploy_as = deploy_as

    def __repr__(self):
        """Convert to string repr."""
        return f"Deploy({self.target} {self.deploy_as})"
