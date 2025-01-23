"""Main file."""
from pathlib import Path

from aisle.lexer.lexer import Lexer
from aisle.parser.parser import Parser


def main():  # pragma: no cover
    """Entrypoint."""
    with Path("../test.aisle").open("r") as f:
        src = f.read()
    lexer = Lexer(src)
    tokens = lexer.scan()
    parser = Parser(src, tokens)
    nodes = parser.parse()
    print(*nodes, sep="\n")


if __name__ == "__main__":
    main()
