"""Main file."""

from pathlib import Path  # pragma: no cover

from aisle.analyser.impl.analyser import Analyser  # pragma: no cover
from aisle.codegen.impl.plantuml import (  # pragma: no cover
    PlantUMLProjectGenerator,
)
from aisle.lexer.impl.lexer import Lexer  # pragma: no cover
from aisle.parser.impl.parser import Parser  # pragma: no cover


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
    gen = PlantUMLProjectGenerator(project)
    Path("context.puml").write_text(gen.generate_context())
    Path("containers.puml").write_text(gen.generate_containers())
    Path("deployment.puml").write_text(gen.generate_deployments())


if __name__ == "__main__":  # pragma: no cover
    main()
