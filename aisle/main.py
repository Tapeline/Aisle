"""Main file."""
import pprint
from pathlib import Path

from aisle.analyser.analyser import Analyser
from aisle.analyser.entities.context import SystemEntity
from aisle.analyser.entities.links import Link
from aisle.analyser.entities.project import Project
from aisle.lexer.lexer import Lexer
from aisle.parser.nodes.links import LinkType
from aisle.parser.parser import Parser


def main():  # pragma: no cover
    """Entrypoint."""
    with Path("../test.aisle").open("r") as f:
        src = f.read()
    # src = (
    #     "scope project Test\n"
    #     "scope context Test\n"
    #     "system TestSystem:\n"
    #     "    description\n"
    #     "    tech = Tech\n"
    #     "    links:\n"
    #     "        --> Test\n"
    #     ""
    # )
    lexer = Lexer(src)
    tokens = lexer.scan()
    parser = Parser(src, tokens)
    nodes = parser.parse()
    analyser = Analyser(nodes)
    project = analyser.analyse()
    for k, v in project.namespace.items():
        print(k, ":", v)
    expected = Project(
        name="Test",
        description="",
        comments=[],
        styling=[],
        namespace={
            "TestSystem": SystemEntity(
                name="TestSystem",
                description="description",
                links=[
                    Link(
                        type=LinkType.OUTGOING,
                        to="Test",
                        over=None,
                        description=""
                    )
                ],
                tags=[]
            )
        }
    )
    pprint.pprint(project, width=120)


if __name__ == "__main__":
    main()
