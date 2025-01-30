"""Main file."""

from pathlib import Path

import click

from aisle.analyser.exceptions import AnalyserException
from aisle.analyser.impl.analyser import Analyser
from aisle.codegen.impl.plantuml import (
    PlantUMLProjectGenerator,
)
from aisle.lexer.exceptions import LexerException
from aisle.lexer.impl.lexer import Lexer
from aisle.parser.exceptions import ParserException
from aisle.parser.impl.parser import Parser


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
@click.argument("file")
def generate(directory, encoding, file):
    """Generate PlantUML diagrams from Aisle file."""
    src = Path(file).read_text(encoding=encoding)
    try:  # noqa: WPS229
        lexer = Lexer(src)
        tokens = lexer.scan()
        parser = Parser(src, tokens)
        nodes = parser.parse()
        analyser = Analyser(nodes)
        project = analyser.analyse()
        generator = PlantUMLProjectGenerator(project)
        directory = directory or project.name
        _generate_and_write(directory, encoding, generator)
        click.echo("Generated")
    except (LexerException, ParserException) as exc:
        _print_error_and_exit(exc.formatted_message)
    except AnalyserException as exc:
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
