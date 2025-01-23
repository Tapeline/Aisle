"""Parser tests."""
from pathlib import Path

from aisle.lexer.lexer import Lexer
from aisle.parser.parser import Parser


def test_with_real_file(snapshot):
    """Test that real project decl is parsed correctly."""
    with Path("./tests/fixtures/test_1.aisle").open("r") as src_file:
        src = src_file.read()
    lexer = Lexer(src)
    tokens = lexer.scan()
    parser = Parser(src, tokens)
    nodes = parser.parse()
    nodes_str = "\n".join(map(str, nodes))
    assert nodes_str == snapshot
