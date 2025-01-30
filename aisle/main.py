"""Main file."""
import pprint
from pathlib import Path

from aisle.analyser.analyser import Analyser
from aisle.analyser.entities.context import SystemEntity
from aisle.analyser.entities.links import Link
from aisle.analyser.entities.project import Project
from aisle.codegen.generator import generate_context, generate_containers, generate_deployments
from aisle.lexer.lexer import Lexer
from aisle.parser.nodes.links import LinkType
from aisle.parser.parser import Parser


def main():  # pragma: no cover
    """Entrypoint."""
    with Path("../dockingjudge.aisle").open("r") as f:
        src = f.read()
    lexer = Lexer(src)
    tokens = lexer.scan()
    parser = Parser(src, tokens)
    nodes = parser.parse()
    analyser = Analyser(nodes)
    project = analyser.analyse()
    Path("context.puml").write_text(generate_context(project))
    Path("containers.puml").write_text(generate_containers(project))
    Path("deployment.puml").write_text(generate_deployments(project))


if __name__ == "__main__":
    main()
