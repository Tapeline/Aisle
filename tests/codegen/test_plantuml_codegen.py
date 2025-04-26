from pathlib import Path

from aisle.analyser.impl.analyser import Analyser
from aisle.codegen.impl.plantuml.plantuml import PlantUMLProjectGenerator
from aisle.codegen.interfaces import AbstractProjectGenerator
from aisle.lexer.impl.lexer import Lexer
from aisle.parser.impl.parser import Parser


def _get_generator(path: str) -> AbstractProjectGenerator:
    src = Path(path).read_text()
    tokens = Lexer(src).scan()
    nodes = Parser(src, tokens).parse()
    project = Analyser(nodes).analyse()
    return PlantUMLProjectGenerator(project)


def test_context_codegen(snapshot):
    """Test that context layer generates correctly."""
    generator = _get_generator("./tests/fixtures/test_1_a.aisle")
    assert generator.generate_context() == snapshot


def test_containers_codegen(snapshot):
    """Test that containers layer generates correctly."""
    generator = _get_generator("./tests/fixtures/test_1_a.aisle")
    assert generator.generate_containers() == snapshot


def test_deployment_codegen(snapshot):
    """Test that deployment layer generates correctly."""
    generator = _get_generator("./tests/fixtures/test_1_a.aisle")
    assert generator.generate_deployments() == snapshot


def test_link_directions_codegen(snapshot):
    """Test that different link directions work correctly."""
    generator = _get_generator("./tests/fixtures/test_2.aisle")
    assert generator.generate_context() == snapshot


def test_name_clashes_codegen(snapshot):
    """Test that clashing names are resolved correctly."""
    generator = _get_generator("./tests/fixtures/test_3.aisle")
    assert generator.generate_context() == snapshot
