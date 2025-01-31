import hashlib
import string
from typing import Final

from aisle.analyser.entities.containers import ServiceEntity
from aisle.analyser.entities.context import ActorEntity, SystemEntity
from aisle.analyser.entities.deployment import DeploymentEntity
from aisle.analyser.entities.links import Link
from aisle.analyser.entities.project import Project, ProjectEntity
from aisle.codegen import utils
from aisle.codegen.interfaces import AbstractProjectGenerator
from aisle.parser.nodes.links import LinkType


class SafeNameStorage:
    """Automatically assigns safe names."""

    def __init__(self) -> None:
        """Create storage."""
        self._names: dict[str, str] = {}

    def __getitem__(self, unsafe_name: str) -> str:
        """Get safe name or generate if not present."""
        if unsafe_name not in self._names:
            self._names[unsafe_name] = _safe_name(unsafe_name)
        return self._names[unsafe_name]


class CodeGenerator:
    """PlantUML code generator."""

    def __init__(self, project: Project):
        """Init generator."""
        self.project = project
        self._safe_names = SafeNameStorage()

    def gen_actor(self, actor: ActorEntity) -> str:
        """Generate actor code."""
        safe_name = self._safe_names[actor.name]
        tags = _compile_tags(actor.tags)
        return (
            f'Person('
            f'{safe_name}, '
            f'"{_safe_str(actor.name)}", '
            f'"{_safe_str(actor.description)}",'
            f'$tags="{tags}"'
            f')'
        )

    def gen_system(self, system: SystemEntity) -> str:
        """Generate system code."""
        safe_name = self._safe_names[system.name]
        tags = _compile_tags(system.tags)
        suffix = "_Ext" if system.is_external else ""
        return (
            f'System{suffix}('
            f'{safe_name}, '
            f'"{_safe_str(system.name)}", '
            f'"{_safe_str(system.description)}",'
            f'$tags="{tags}"'
            f')'
        )

    def gen_service(self, service: ServiceEntity) -> str:
        """Generate service (container) code."""
        safe_name = self._safe_names[service.name]
        tags = _compile_tags(service.tags)
        suffix = "_Ext" if service.is_external else ""
        return (
            f'Container{suffix}('
            f'{safe_name}, '
            f'"{_safe_str(service.name)}", '
            f'"{_safe_str(service.description)}",'
            f'$tags="{tags}"'
            f')'
        )

    def gen_system_internals(self, system: SystemEntity) -> str:
        """Generate system boundary with containers."""
        services = self.project.get_services_of_system(system.name)
        service_gen = "\n".join(map(self.gen_service, services))
        safe_name = self._safe_names[system.name]
        boundary = (
            f'System_Boundary('
            f'{safe_name},'
            f'"{_safe_str(system.name)}"'
            f')'
        )
        return (
            boundary +
            "{\n" +
            utils.indent(service_gen, 4) +
            "\n}"
        )

    def gen_link(self, link_from: ProjectEntity, link: Link) -> str:
        """Generate link code."""
        safe_name_a = self._safe_names[link_from.name]
        safe_name_b = self._safe_names[link.to]
        link_str = ""
        if link.type == LinkType.OUTGOING:
            link_str = (
                f'Rel('
                f'{safe_name_a}, '
                f'{safe_name_b}, '
                f'"{_safe_str(link.description)}",'
                f'"{_safe_str(link.over)}"'
                f')'
            )
        if link.type == LinkType.INCOMING:
            link_str = (
                f'Rel('
                f'{safe_name_b}, '
                f'{safe_name_a}, '
                f'"{_safe_str(link.description)}",'
                f'"{_safe_str(link.over)}"'
                f')'
            )
        if link.type in {LinkType.BIDIRECTIONAL, LinkType.NON_DIRECTED}:
            link_str = (
                f'BiRel('
                f'{safe_name_b}, '
                f'{safe_name_a}, '
                f'"{_safe_str(link.description)}",'
                f'"{_safe_str(link.over)}"'
                f')'
            )
        return link_str

    def gen_deployment(self, deployment: DeploymentEntity) -> str:
        """Generate deployment code."""
        code: list[str] = []
        code += map(self.gen_deployment, deployment.inner_entities)
        for svc_deployment in deployment.deploys:
            code.append(
                f'Node('
                f'{self._safe_names[svc_deployment.service_name]},'
                f'"{_safe_str(svc_deployment.service_name)}",'
                f'$descr="{_safe_str(svc_deployment.deploy_as)}"'
                f')'
            )
        return (
            f'Boundary('
            f'{self._safe_names[deployment.name]},'
            f'"{_safe_str(deployment.name)}",'
            f'$descr="{_safe_str(deployment.description)}"'
            f')' +
            "{\n" +
            utils.indent("\n".join(code), 4) +
            "\n}"
        )

    def gen_context_map(self) -> str:  # noqa: WPS210
        """Generate context code."""
        code: list[str] = []
        relations: list[tuple[ProjectEntity, Link]] = []
        for actor in self.project.get_actors():
            code.append(self.gen_actor(actor))
            relations.extend((actor, rel) for rel in actor.links)
        for system in self.project.get_systems():
            code.append(self.gen_system(system))
            relations.extend((system, rel) for rel in system.links)
        for entity, rel in relations:
            code.append(self.gen_link(entity, rel))
        return "\n\n".join(code)

    def gen_container_map(self) -> str:  # noqa: WPS210
        """Generate container code."""
        imported_actors = []
        code = []
        relations = []
        used_entities = set()
        for system in self.project.get_systems():
            code.append(self.gen_system_internals(system))
            for service in self.project.get_services_of_system(system.name):
                used_entities.add(service.name)
                for rel in service.links:
                    relations.append((service, rel))
                    entity = self.project.namespace[rel.to]
                    if isinstance(entity, ActorEntity):
                        imported_actors.append(entity)  # noqa: WPS220
        code.extend(map(self.gen_actor, imported_actors))
        for entity, rel in relations:
            code.append(self.gen_link(entity, rel))
        return "\n\n".join(code)

    def gen_deployment_map(self) -> str:
        """Generate deployment code."""
        code = list(map(self.gen_deployment, self.project.get_deployments()))
        return "\n\n".join(code)


_ALLOWED_CHARS: Final = (
    string.ascii_letters +
    string.digits +
    "_"
)


def _safe_name(name: str) -> str:
    """Ensure name is safe to use as identifier."""
    name = name.replace(" ", "_")
    filtered_name = "".join(char for char in name if char in _ALLOWED_CHARS)
    hash_part = hashlib.md5(name.encode()).hexdigest()[:8]
    if filtered_name == name:
        return filtered_name
    return f"{filtered_name}_{hash_part}"


def _compile_tags(tags: list[str]) -> str:
    """Join all tags with +."""
    return "+".join(map(_safe_name, tags))


def _safe_str(text: str | None) -> str:
    r"""Get rid of unsafe string chars like " or \n."""
    if text is None:
        return ""
    return text.replace('"', r'\"').replace("\n", r"\n")


class PlantUMLProjectGenerator(AbstractProjectGenerator):
    """PlantUML code generator."""

    file_extension = "puml"

    def __init__(self, project: Project) -> None:
        """Create generator."""
        self.project = project
        self._cg = CodeGenerator(project)

    def generate_context(self) -> str:
        """Generate context code."""
        return (
            f"@startuml\n"
            f"!include <C4/C4_Context>\n"
            f"{self._cg.gen_context_map()}\n"
            f"@enduml\n"
        )

    def generate_containers(self) -> str:
        """Generate containers code."""
        return (
            f"@startuml\n"
            f"!include <C4/C4_Container>\n"
            f"{self._cg.gen_container_map()}\n"
            f"@enduml\n"
        )

    def generate_deployments(self) -> str:
        """Generate deployment code."""
        return (
            f"@startuml\n"
            f"!include <C4/C4_Deployment>\n"
            f"{self._cg.gen_deployment_map()}\n"
            f"@enduml\n"
        )
