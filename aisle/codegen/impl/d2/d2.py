import textwrap
from collections.abc import Mapping
from typing import assert_never

from aisle.analyser.entities.containers import ServiceEntity
from aisle.analyser.entities.context import ActorEntity, SystemEntity
from aisle.analyser.entities.deployment import DeploymentEntity
from aisle.analyser.entities.links import Link
from aisle.analyser.entities.project import Project
from aisle.codegen.impl.d2.text_utils import safe_name
from aisle.codegen.interfaces import AbstractProjectGenerator, FileGenerator
from aisle.parser.nodes.links import LinkType


class _D2SafeNameStorage:
    """Automatically assigns safe names according to d2."""

    def __init__(self) -> None:
        """Create storage."""
        self._names: dict[str, str] = {}

    def __getitem__(self, unsafe_name: str) -> str:
        """Get safe name or generate if not present."""
        if unsafe_name not in self._names:
            self._names[unsafe_name] = safe_name(unsafe_name)
        return self._names[unsafe_name]

    @property
    def names(self) -> dict[str, str]:
        return self._names


class _CodeGenerator:
    def __init__(self, project: Project) -> None:
        """Create generator."""
        self.project = project
        self._safe_names = _D2SafeNameStorage()

    def get_main_map(self) -> str:
        """Generate main view."""
        strings: list[str] = []
        strings.extend(
            self._gen_actor(actor)
            for actor in self.project.get_actors()
        )
        strings.extend(
            self._gen_system(system)
            for system in self.project.get_systems()
        )
        strings.append(self._gen_links())
        return "\n\n".join(strings)

    def get_deployment_map(self) -> str:
        return "\n\n".join(self._gen_deployments())

    def _gen_system(self, system: SystemEntity) -> str:
        sys_name = self._safe_names[system.name]
        sys_desc = textwrap.indent(system.description, "  ")
        short_desc = textwrap.indent(_gen_short_desc(system), "  ")
        system_code = (
            f"{sys_name}: |md\n"
            f"  ## {system.name}\n"
            f"{short_desc}\n\n"
            f"{sys_desc}\n"
            "| {\n"
            "  shape: rectangle\n"
            "  label.near: bottom-left\n"
            "}\n"
        )
        services = [
            self._gen_service(system, service)
            for service in self.project.get_services_of_system(system.name)
        ]
        return "\n\n".join([system_code, *services])

    def _gen_service(
            self, system: SystemEntity, service: ServiceEntity
    ) -> str:
        svc_name = self._safe_names[service.name]
        sys_name = self._safe_names[system.name]
        svc_desc = textwrap.indent(service.description, "  ")
        short_desc = textwrap.indent(_gen_short_desc(service), "  ")
        svc_shape = _get_service_shape(service)
        return (
            f"{sys_name}.{svc_name}: |md\n"
            f"  ## {service.name}\n"
            f"{short_desc}\n\n"
            f"{svc_desc}\n"
            "| {\n"
            f"  shape: {svc_shape}\n"
            "}\n"
        )

    def _gen_actor(self, actor: ActorEntity) -> str:
        actor_name = self._safe_names[actor.name]
        actor_desc = textwrap.indent(actor.description, "  ")
        short_desc = textwrap.indent(_gen_short_desc(actor), "  ")
        return (
            f"{actor_name}: |md\n"
            f"  ## {actor.name}\n"
            f"{short_desc}\n\n"
            f"{actor_desc}\n"
            "| {\n"
            "  shape: c4-person\n"
            "}\n"
        )

    def _get_d2_names_map(self) -> Mapping[str, str]:
        names = self._safe_names.names.copy()
        for system in self.project.get_systems():
            for service in self.project.get_services_of_system(system.name):
                names[service.name] = (
                    f"{names[system.name]}.{self._safe_names[service.name]}"
                )
        return names

    def _gen_links(self) -> str:
        links: list[str] = []
        names = self._get_d2_names_map()
        for actor in self.project.get_actors():
            links.extend(
                _gen_link(
                    names[actor.name], names[link.to], link
                )
                for link in actor.links
            )
        for system in self.project.get_systems():
            links.extend(
                _gen_link(
                    names[system.name], names[link.to], link
                )
                for link in system.links
            )
            for service in self.project.get_services_of_system(system.name):
                links.extend(
                    _gen_link(
                        names[service.name], names[link.to], link
                    )
                    for link in service.links
                )
        return "\n".join(links)

    def _gen_deployments(self) -> list[str]:
        return [
            "\n\n".join(
                _gen_deployment_rec(self._safe_names, [], deployment)
            )
            for deployment in self.project.get_deployments()
        ]


def _gen_deployment_rec(  # noqa: WPS210
        safe_names: _D2SafeNameStorage,
        prefix: list[str],
        deployment: DeploymentEntity
) -> list[str]:
    dep_name = safe_names[deployment.name]
    dep_desc = textwrap.indent(deployment.description, "  ")
    short_desc = textwrap.indent(_gen_short_desc(deployment), "  ")
    qualname = ".".join([*prefix, dep_name])
    dep_code = (
        f"{qualname}: |md\n"
        f"  ## {deployment.name}\n"
        f"{short_desc}\n\n"
        f"{dep_desc}\n"
        "| {\n"
        "  shape: rectangle\n"
        "  label.near: bottom-left\n"
        "}\n"
    )
    deployments = [dep_code]
    deployments.extend(
        (
            f"{qualname}.{safe_names[service.service_name]}: |md\n"
            f"  ### {service.service_name}\n"
            f"  deploy as {service.deploy_as}\n"
            "| {\n"
            "  shape: rectangle\n"
            "}\n"
        )
        for service in deployment.deploys
    )
    for sub_dep in deployment.inner_entities:
        deployments.extend(
            _gen_deployment_rec(safe_names, [*prefix, dep_name], sub_dep)
        )
    return deployments


def _gen_short_desc(
        entity: SystemEntity | ServiceEntity | ActorEntity | DeploymentEntity
) -> str:
    if isinstance(entity, SystemEntity):
        is_ext = " (external)" if entity.is_external else ""
        return f"[Software System{is_ext}]"
    if isinstance(entity, ServiceEntity):
        is_ext = " (external)" if entity.is_external else ""
        return f"[Container{is_ext}: {entity.tech}]"
    if isinstance(entity, ActorEntity):
        return "[Actor]"
    if isinstance(entity, DeploymentEntity):
        return "[Deployment]"
    assert_never(entity)


def _get_service_shape(service: ServiceEntity) -> str:
    if "db" in service.tags or "database" in service.tags:
        return "cylinder"
    return "rectangle"


def _gen_link(from_name: str, to_name: str, link: Link) -> str:
    link_t = {
        LinkType.OUTGOING: "->",
        LinkType.INCOMING: "<-",
        LinkType.BIDIRECTIONAL: "<->",
        LinkType.NON_DIRECTED: "<->",
    }[link.type]
    link_desc = []
    if link.over:
        link_desc.append(f"[{link.over}]")
    if link.description:
        link_desc.append(repr(link.description).strip("'"))
    link_desc_s = " ".join(link_desc)
    return f'{from_name} {link_t} {to_name}: "{link_desc_s}"'


class D2ProjectGenerator(AbstractProjectGenerator):
    """D2lang code generator."""

    file_extension = "d2"

    def __init__(self, project: Project) -> None:
        """Create generator."""
        self.project = project
        self._cg = _CodeGenerator(project)

    @property
    def file_generators(self) -> Mapping[str, FileGenerator]:
        """Get generators."""
        return {
            "main": self.generate_main,
            "deployments": self.generate_deployments
        }

    def generate_main(self) -> str:
        """Generate code."""
        return self._cg.get_main_map()

    def generate_deployments(self) -> str:
        """Generate code for deployments."""
        return self._cg.get_deployment_map()
