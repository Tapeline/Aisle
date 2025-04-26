import pytest

from aisle.analyser.entities.project import NameNotFoundError
from aisle.analyser.impl.analyser import Analyser
from aisle.codegen.impl.plantuml.plantuml import PlantUMLProjectGenerator
from aisle.lexer.impl.lexer import Lexer
from aisle.parser.impl.parser import Parser


def test_no_name_found():
    """Test that undefined name raises corresponding error."""
    src = (
        "scope project Proj\n"
        "scope context Proj\n"
        "system A:\n"
        "    ddd\n"
        "scope containers Proj\n"
        "service B:\n"
        "    system = A\n"
        "    links:\n"
        "        --> Undefined\n"
    )
    tokens = Lexer(src).scan()
    nodes = Parser(src, tokens).parse()
    project = Analyser(nodes).analyse()
    cg = PlantUMLProjectGenerator(project)
    with pytest.raises(NameNotFoundError):
        cg.generate_containers()
