from aisle.parser.nodes.base import Node


class VisitMethodNotFoundError(AttributeError):
    def __init__(self, class_name: str, obj):  # pragma: no cover
        super().__init__(obj=obj, name=f"Method visit_{class_name}")
        self.class_name = class_name


class AnalyserException(Exception):
    default_message: str = "Invalid node"

    def __init__(
            self,
            node: Node,
            message: str | None = None,
            **params,
    ):
        self.node = node
        self.message = message or self.default_message
        for param_k, param_v in params.items():
            setattr(self, param_k, param_v)

    def formatted_message(self, source_code: str):
        lines = source_code.splitlines()
        formatted = self.message.format(node=self.node)
        return (
            f"Exception while analysing node {self.node}\n"
            f"At line: {self.node.line}\n"
            f"{self.node.line} |  {lines[self.node.line - 1]}\n"
            f"{formatted}"
        )


class NoProjectDefinedException(AnalyserException):
    default_message: str = (
        "Found {node.__class__.__name__} node, but no project was defined. "
        "Define a project first!"
    )


class DuplicateProjectDefinitionException(AnalyserException):
    default_message: str = (
        "Found project definition, but project was already defined."
    )


class UnmatchedProjectAndScopeNameException(AnalyserException):
    default_message: str = (
        "Found scope with '{scope_name}', "
        "but project is called '{project_name}'"
    )


class UnmatchedScopeAndEntityTypeException(AnalyserException):
    default_message: str = (
        "In {scope_type} scope, there was found "
        "an entity of {entity_type} type"
    )
