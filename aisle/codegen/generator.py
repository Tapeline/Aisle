import hashlib
import shlex
import string
import textwrap
from typing import Final

from aisle.analyser.entities.context import ActorEntity, SystemEntity
from aisle.analyser.entities.containers import ServiceEntity
from aisle.analyser.entities.deployment import DeploymentEntity
from aisle.analyser.entities.links import Link
from aisle.analyser.entities.project import Project, ProjectEntity
from aisle.parser.nodes.links import LinkType


class SafeNameStorage:
    def __init__(self):
        self._names: dict[str, str] = {}

    def __getitem__(self, item) -> str:
        if item not in self._names:
            self._names[item] = _safe_name(item)
        return self._names[item]


class CodeGenerator:
    def __init__(self, project: Project):
        self.project = project
        self._safe_names = SafeNameStorage()

    def gen_actor(self, actor: ActorEntity) -> str:
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
        services = self.project.get_services_of_system(system.name)
        service_gen = "\n".join(map(self.gen_service, services))
        safe_name = self._safe_names[system.name]
        boundary = (
            f'System_Boundary('
            f'{safe_name},'
            f'"{_safe_str(system.name)}"'
            f')'
        )
        return boundary + "{\n" + _indent(service_gen, 4) + "\n}"

    def gen_link(self, link_from: ProjectEntity, link: Link) -> str:
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
        if (
                link.type == LinkType.BIDIRECTIONAL
                or link.type == LinkType.NON_DIRECTED
        ):
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
        code = []
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
            f')'
            + "{\n"
            + _indent("\n".join(code), 4)
            + "\n}"
        )

    def gen_context_map(self) -> str:
        code = []
        relations = []
        for actor in self.project.get_actors():
            code.append(self.gen_actor(actor))
            for rel in actor.links:
                relations.append((actor, rel))
        for system in self.project.get_systems():
            code.append(self.gen_system(system))
            for rel in system.links:
                relations.append((system, rel))
        for entity, rel in relations:
            code.append(self.gen_link(entity, rel))
        return "\n\n".join(code)

    def gen_container_map(self) -> str:
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
                        imported_actors.append(entity)
        for actor in imported_actors:
            code.append(self.gen_actor(actor))
        for entity, rel in relations:
            code.append(self.gen_link(entity, rel))
        return "\n\n".join(code)

    def gen_deployment_map(self) -> str:
        code = []
        for deployment in self.project.get_deployments():
            code.append(self.gen_deployment(deployment))
        return "\n\n".join(code)


_ALLOWED_CHARS: Final = string.ascii_letters + string.digits + "_"


def _safe_name(name: str) -> str:
    name = name.replace(" ", "_")
    filtered_name = "".join(char for char in name if char in _ALLOWED_CHARS)
    hash_part = hashlib.md5(name.encode()).hexdigest()[:8]
    if filtered_name == name:
        return filtered_name
    return f"{filtered_name}_{hash_part}"


def _indent(text: str, indent_level: int) -> str:
    return textwrap.indent(text, prefix=" " * indent_level)


def _compile_tags(tags: list[str]) -> str:
    return "+".join(map(_safe_name, tags))


def _safe_str(text: str) -> str:
    if text is None:
        return ""
    return text.replace('"', '\\"').replace("\n", "\\n")


def generate_context(project: Project) -> str:
    cg = CodeGenerator(project)
    return (
        f'@startuml\n'
        f'!include <C4/C4_Context>\n'
        f'{cg.gen_context_map()}\n'
        f'@enduml\n'
    )


def generate_containers(project: Project) -> str:
    cg = CodeGenerator(project)
    return (
        f'@startuml\n'
        f'!include <C4/C4_Container>\n'
        f'{cg.gen_container_map()}\n'
        f'@enduml\n'
    )


def generate_deployments(project: Project) -> str:
    cg = CodeGenerator(project)
    return (
        f'@startuml\n'
        f'!include <C4/C4_Deployment>\n'
        f'{cg.gen_deployment_map()}\n'
        f'@enduml\n'
    )
