from pathlib import Path

from aisle.analyser.impl.analyser import Analyser
from aisle.codegen.impl.d2.d2 import D2ProjectGenerator
from aisle.codegen.interfaces import AbstractProjectGenerator
from aisle.lexer.impl.lexer import Lexer
from aisle.parser.impl.parser import Parser


def _get_generator(path: str) -> AbstractProjectGenerator:
    src = Path(path).read_text()
    tokens = Lexer(src).scan()
    nodes = Parser(src, tokens).parse()
    project = Analyser(nodes).analyse()
    return D2ProjectGenerator(project)


def test_main_codegen(snapshot):
    """Test that context and container layers generate correctly."""
    generator = _get_generator("./tests/fixtures/test_1_a.aisle")
    assert generator.file_generators["main"]() == snapshot


def test_deployments_codegen(snapshot):
    """Test that deployment layer generates correctly."""
    generator = _get_generator("./tests/fixtures/test_1_a.aisle")
    assert generator.file_generators["deployments"]() == snapshot


def test_link_directions_codegen(snapshot):
    """Test that different link directions work correctly."""
    generator = _get_generator("./tests/fixtures/test_2.aisle")
    assert generator.file_generators["main"]() == snapshot


def test_name_clashes_codegen(snapshot):
    """Test that clashing names are resolved correctly."""
    generator = _get_generator("./tests/fixtures/test_3.aisle")
    assert generator.file_generators["main"]() == snapshot
