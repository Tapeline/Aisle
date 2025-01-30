from pathlib import Path

from aisle.analyser.analyser import Analyser
from aisle.analyser.entities.project import Project
from aisle.codegen.generator import (
    generate_context,
    generate_containers,
    generate_deployments
)
from aisle.lexer.lexer import Lexer
from aisle.parser.parser import Parser


def _read_project(path: str) -> Project:
    src = Path(path).read_text()
    tokens = Lexer(src).scan()
    nodes = Parser(src, tokens).parse()
    project = Analyser(nodes).analyse()
    return project


def test_context_codegen(snapshot):
    """Test that context layer generates correctly."""
    project = _read_project("./tests/fixtures/test_1_a.aisle")
    assert generate_context(project) == snapshot


def test_containers_codegen(snapshot):
    """Test that containers layer generates correctly."""
    project = _read_project("./tests/fixtures/test_1_a.aisle")
    assert generate_containers(project) == snapshot


def test_deployment_codegen(snapshot):
    """Test that deployment layer generates correctly."""
    project = _read_project("./tests/fixtures/test_1_a.aisle")
    assert generate_deployments(project) == snapshot


def test_link_directions_codegen(snapshot):
    """Test that different link directions work correctly."""
    project = _read_project("./tests/fixtures/test_2.aisle")
    assert generate_context(project) == snapshot


def test_name_clashes_codegen(snapshot):
    """Test that clashing names are resolved correctly."""
    project = _read_project("./tests/fixtures/test_3.aisle")
    assert generate_context(project) == snapshot
