"""Main file."""

from pathlib import Path
from types import MappingProxyType

import click

from aisle.analyser.exceptions import AnalyserError
from aisle.analyser.impl.analyser import Analyser
from aisle.codegen.impl.mermaid import MermaidProjectGenerator
from aisle.codegen.impl.plantuml import (
    PlantUMLProjectGenerator,
)
from aisle.lexer.exceptions import LexerError
from aisle.lexer.impl.lexer import Lexer
from aisle.parser.exceptions import ParserError
from aisle.parser.impl.parser import Parser

_GENERATORS = MappingProxyType({
    "plantuml": PlantUMLProjectGenerator,
    "mermaid": MermaidProjectGenerator,
})
_GENERATOR_NAMES = tuple(map(str, _GENERATORS.keys()))


@click.group()
def aisle():
    """Aisle command line tool."""


@aisle.command(name="generate")
@click.option(
    "--directory",
    default=None,
    help="directory to place generated files"
)
@click.option(
    "--encoding",
    default=None,
    help="directory to place generated files"
)
@click.option(
    "--fmt",
    default="plantuml",
    help="output code format"
)
@click.argument("file")
def generate(directory, encoding, file, fmt):
    """Generate PlantUML diagrams from Aisle file."""
    src = Path(file).read_text(encoding=encoding)
    if fmt not in _GENERATORS:
        _print_error_and_exit(
            f"{fmt} not found! Available formats: {_GENERATOR_NAMES}"
        )
    try:  # noqa: WPS229
        lexer = Lexer(src)
        tokens = lexer.scan()
        parser = Parser(src, tokens)
        nodes = parser.parse()
        analyser = Analyser(nodes)
        project = analyser.analyse()
        generator = _GENERATORS[fmt](project)
        directory = directory or project.name
        _generate_and_write(directory, encoding, generator)
        click.echo("Generated")
    except (LexerError, ParserError) as exc:
        _print_error_and_exit(exc.formatted_message)
    except AnalyserError as exc:
        _print_error_and_exit(exc.formatted_message(src))


def _print_error_and_exit(text: str) -> None:
    click.echo(
        click.style(text, fg="red"),
        err=True,
        color=True
    )
    raise click.exceptions.Exit(1)


def _generate_and_write(directory, encoding, generator):
    Path(directory).mkdir(parents=True, exist_ok=True)
    Path(
        directory,
        f"context.{generator.file_extension}"
    ).write_text(
        generator.generate_context(),
        encoding=encoding
    )
    Path(
        directory,
        f"containers.{generator.file_extension}"
    ).write_text(
        generator.generate_containers(),
        encoding=encoding
    )
    Path(
        directory,
        f"deployment.{generator.file_extension}"
    ).write_text(
        generator.generate_deployments(),
        encoding=encoding
    )


def main():
    """Entrypoint."""
    aisle()


if __name__ == "__main__":  # pragma: no cover
    main()
