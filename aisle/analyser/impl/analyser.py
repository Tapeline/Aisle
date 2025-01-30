from collections.abc import Sequence
from dataclasses import dataclass
from types import MappingProxyType

from aisle.analyser.entities.containers import ServiceEntity
from aisle.analyser.entities.context import ActorEntity, SystemEntity
from aisle.analyser.entities.deployment import (
    DeploymentEntity,
    ServiceDeployment,
)
from aisle.analyser.entities.links import Link
from aisle.analyser.entities.project import Project
from aisle.analyser.entities.styling import LegendStyling, StylingAttributes
from aisle.analyser.exceptions import (
    DuplicateProjectDefinitionException,
    NoProjectDefinedException,
    UnmatchedProjectAndScopeNameException,
    UnmatchedScopeAndEntityTypeException,
    VisitMethodNotFoundError,
)
from aisle.analyser.interfaces import AbstractAnalyser
from aisle.parser.nodes.attribute import AttrNode
from aisle.parser.nodes.base import Node
from aisle.parser.nodes.entity import (
    DeployNode,
    EntityNode,
    EntityType,
    ProjectDefNode,
)
from aisle.parser.nodes.legend import LegendDeclarationNode
from aisle.parser.nodes.links import LinkCollectionNode, LinkNode
from aisle.parser.nodes.scope import ScopeNode, ScopeType
from aisle.parser.nodes.text import TextNode


class _AnalyserBase:
    def _visit(self, node: Node):
        class_name = node.__class__.__name__
        self._pre_visit(node)
        try:
            getattr(self, f"_visit_{class_name}")(node)
        except AttributeError as error:  # pragma: no cover
            raise VisitMethodNotFoundError(class_name, self) from error

    def _pre_visit(self, node: Node):
        ...  # pragma: no cover


@dataclass
class Scope:
    """Analyser scope."""

    type: ScopeType
    name: str


_ALLOWED_ENTITY_TYPES = MappingProxyType({
    ScopeType.CONTEXT: {EntityType.ACTOR, EntityType.SYSTEM},
    ScopeType.CONTAINERS: {EntityType.SERVICE},
    ScopeType.DEPLOYMENT: {EntityType.DEPLOYMENT},
})


class Analyser(AbstractAnalyser, _AnalyserBase):
    """Default analyser impl."""

    def __init__(self, nodes: Sequence[Node]):
        """Create analyser."""
        self.project: Project | None = None
        self.scope: Scope | None = None
        self.nodes = nodes

    def analyse(self) -> Project:
        """Analyse AST and create project."""
        for node in self.nodes:
            self._visit(node)
        if self.project is None:
            raise NoProjectDefinedException(
                Node(0),
                message="No project found"
            )
        return self.project

    def _pre_visit(self, node: Node):
        if self.project is None and not isinstance(node, ProjectDefNode):
            raise NoProjectDefinedException(node)

    def _visit_ProjectDefNode(self, node: ProjectDefNode):
        if self.project is not None:
            raise DuplicateProjectDefinitionException(node)
        description = "\n".join(node.description)
        self.project = Project(
            name=node.name,
            description=description,
            namespace={},
            styling=[],
            comments=[]
        )

    def _visit_ScopeNode(self, node: ScopeNode):
        if self.project.name != node.scope_name:
            raise UnmatchedProjectAndScopeNameException(
                node,
                scope_name=node.scope_name,
                project_name=self.project.name
            )
        self.scope = Scope(node.scope_type, node.scope_name)

    def _ensure_entity_applicable(  # pragma: no cover
            self,
            entity: EntityNode
    ):
        if self.scope is None:
            raise UnmatchedScopeAndEntityTypeException(
                entity,
                scope_type=None,
                entity_type=entity.type.value
            )
        if entity.type not in _ALLOWED_ENTITY_TYPES[self.scope.type]:
            raise UnmatchedScopeAndEntityTypeException(
                entity,
                scope_type=self.scope.type.value,
                entity_type=entity.type.value
            )

    def _visit_EntityNode(self, node: EntityNode):
        self._ensure_entity_applicable(node)
        match node.type:
            case EntityType.ACTOR:
                self._create_actor(node)
            case EntityType.SYSTEM:
                self._create_system(node)
            case EntityType.SERVICE:
                self._create_service(node)
            case EntityType.DEPLOYMENT:
                self._create_deployment(node)

    def _evaluate_entity_body(
            self, body: Sequence[Node]
    ) -> tuple[str, list[Link], dict[str, str]]:
        description = "\n".join(
            node.text for node in body if isinstance(node, TextNode)
        )
        attrs = {
            node.name: node.value
            for node in body if isinstance(node, AttrNode)
        }
        collected_links: list[LinkNode] = []
        for node in body:
            if isinstance(node, LinkCollectionNode):
                collected_links.extend(node.links)
        links = [
            Link(
                type=link.type,
                to=link.to,
                over=link.over,
                description="\n".join(link.description)
            )
            for link in collected_links
        ]
        return description, links, attrs

    def _evaluate_deployment_body(
            self,
            body: Sequence[Node]
    ) -> tuple[str, list[ServiceDeployment], list[DeploymentEntity]]:
        description = "\n".join(
            node.text for node in body if isinstance(node, TextNode)
        )
        svc_deployments = [
            ServiceDeployment(node.target, node.deploy_as)
            for node in body if isinstance(node, DeployNode)
        ]
        inner_deployments = []
        for node in body:
            if not (
                    isinstance(node, EntityNode)
                    and node.type == EntityType.DEPLOYMENT
            ):
                continue
            i_desc, i_svc, i_inner = self._evaluate_deployment_body(node.body)
            inner_deployments.append(DeploymentEntity(
                name=node.name,
                description=i_desc,
                tags=list(node.tags),
                is_external=node.is_external,
                deploys=i_svc,
                inner_entities=i_inner
            ))
        return description, svc_deployments, inner_deployments

    def _create_actor(self, node: EntityNode):
        description, links, _ = self._evaluate_entity_body(node.body)
        entity = ActorEntity(
            name=node.name,
            description=description,
            links=links,
            tags=list(node.tags)
        )
        self.project.namespace[entity.name] = entity

    def _create_system(self, node: EntityNode):
        description, links, _ = self._evaluate_entity_body(node.body)
        entity = SystemEntity(
            name=node.name,
            description=description,
            links=links,
            tags=list(node.tags),
            is_external=node.is_external
        )
        self.project.namespace[entity.name] = entity

    def _create_service(self, node: EntityNode):
        description, links, attrs = self._evaluate_entity_body(node.body)
        entity = ServiceEntity(
            name=node.name,
            description=description,
            links=links,
            tech=attrs.get("tech"),
            system=attrs.get("system"),
            tags=list(node.tags),
            is_external=node.is_external
        )
        self.project.namespace[entity.name] = entity

    def _create_deployment(self, node: EntityNode):
        description, svc_deploys, inner_entities = (
            self._evaluate_deployment_body(node.body)
        )
        entity = DeploymentEntity(
            name=node.name,
            description=description,
            deploys=svc_deploys,
            tags=list(node.tags),
            is_external=node.is_external,
            inner_entities=inner_entities
        )
        self.project.namespace[entity.name] = entity

    def _visit_TextNode(self, node: TextNode):
        self.project.comments.append(node.text)

    def _visit_LegendDeclarationNode(self, node: LegendDeclarationNode):
        description, _, attrs = self._evaluate_entity_body(node.body)
        style = LegendStyling(
            selector=node.selector,
            description=description,
            attrs=StylingAttributes(**attrs)
        )
        self.project.styling.append(style)
