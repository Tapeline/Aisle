"""Main file."""
from os import PathLike
from pathlib import Path
from types import MappingProxyType

import click

from aisle.analyser.exceptions import AnalyserError
from aisle.analyser.impl.analyser import Analyser
from aisle.codegen.impl.d2.d2 import D2ProjectGenerator
from aisle.codegen.impl.mermaid import MermaidProjectGenerator
from aisle.codegen.impl.plantuml.plantuml import (
    PlantUMLProjectGenerator,
)
from aisle.codegen.interfaces import AbstractProjectGenerator
from aisle.lexer.exceptions import LexerError
from aisle.lexer.impl.lexer import Lexer
from aisle.parser.exceptions import ParserError
from aisle.parser.impl.parser import Parser

_GENERATORS = MappingProxyType({
    "plantuml": PlantUMLProjectGenerator,
    "mermaid": MermaidProjectGenerator,
    "d2": D2ProjectGenerator
})
_GENERATOR_NAMES = tuple(map(str, _GENERATORS.keys()))


@click.group()
def aisle() -> None:
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
def generate(directory, encoding, file, fmt) -> None:  # type: ignore
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
        generator = _GENERATORS[fmt](project)  # type: ignore
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


def _generate_and_write(
        directory: PathLike[str],
        encoding: str | None,
        generator: AbstractProjectGenerator
) -> None:
    Path(directory).mkdir(parents=True, exist_ok=True)
    for file_name, gen_func in generator.file_generators.items():
        Path(
            directory,
            f"{file_name}.{generator.file_extension}"
        ).write_text(
            gen_func(),
            encoding=encoding
        )


def main() -> None:
    """Entrypoint."""
    aisle()


if __name__ == "__main__":  # pragma: no cover
    main()
