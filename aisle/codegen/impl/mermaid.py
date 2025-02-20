from aisle.analyser.entities.project import Project
from aisle.codegen import utils
from aisle.codegen.impl import plantuml
from aisle.codegen.interfaces import AbstractProjectGenerator


class MermaidProjectGenerator(AbstractProjectGenerator):
    """Mermaid format generator."""

    file_extension = "txt"

    def __init__(self, project: Project) -> None:
        """Create generator."""
        self.project = project
        self._plantuml = plantuml.CodeGenerator(project)

    def generate_context(self) -> str:
        """Generate context code."""
        return (
            "C4Context\n" +
            utils.indent(
                _rm_empty_tags(self._plantuml.gen_context_map()),
                4
            )
        )

    def generate_containers(self) -> str:
        """Generate containers code."""
        return (
            "C4Container\n" +
            utils.indent(
                _rm_empty_tags(self._plantuml.gen_container_map()),
                4
            )
        )

    def generate_deployments(self) -> str:
        """Generate deployments code."""
        return (
            "C4Deployment\n" +
            utils.indent(
                _rm_empty_tags(self._plantuml.gen_deployment_map()),
                4
            )
        )


def _rm_empty_tags(text: str) -> str:
    return text.replace('$tags=""', "").replace(',$techn=""', "")
