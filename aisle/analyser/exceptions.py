from aisle.exceptions import AisleError
from aisle.parser.nodes.base import Node


class VisitMethodNotFoundError(AttributeError):
    """Raised when tried to visit node, but did not find a suitable method."""

    def __init__(self, class_name: str, target_object):  # pragma: no cover
        """Create exception."""
        super().__init__(
            obj=target_object,
            name=f"Method visit_{class_name}"
        )
        self.class_name = class_name


class AnalyserError(AisleError):
    """Base for analyser exceptions."""

    default_message: str = "Invalid node"

    def __init__(
            self,
            node: Node,
            message: str | None = None,
            **params,  # noqa: WPS110
    ):
        """Create analyser exception and format message."""
        self.node = node
        self.message = message or self.default_message
        for param_k, param_v in params.items():
            setattr(self, param_k, param_v)

    def formatted_message(self, source_code: str):
        """Get beautiful message."""
        lines = source_code.splitlines()
        formatted = self.message.format(node=self.node)
        return (
            f"Exception while analysing node {self.node}\n"  # noqa: WPS237
            f"At line: {self.node.line}\n"
            f"{self.node.line} |  {lines[self.node.line - 1]}\n"
            f"{formatted}"
        )


class NoProjectDefinedError(AnalyserError):
    """Raised when no project was defined."""

    default_message: str = (
        "Found {node.__class__.__name__} node, but no project was defined. "
        "Define a project first!"
    )


class DuplicateProjectDefinitionError(AnalyserError):
    """Raised when >1 project defs found."""

    default_message: str = (
        "Found project definition, but project was already defined."
    )


class UnmatchedProjectAndScopeNameError(AnalyserError):
    """Raised when scope name does not match project name."""

    default_message: str = (
        "Found scope with '{scope_name}', "
        "but project is called '{project_name}'"
    )


class UnmatchedScopeAndEntityTypeError(AnalyserError):
    """Raised when declared entity is incompatible with scope."""

    default_message: str = (
        "In {scope_type} scope, there was found "
        "an entity of {entity_type} type"
    )
