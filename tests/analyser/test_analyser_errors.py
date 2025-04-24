import pytest

from aisle.analyser.exceptions import (
    DuplicateProjectDefinitionError,
    NoProjectDefinedError,
    UnmatchedProjectAndScopeNameError,
)
from aisle.analyser.impl.analyser import Analyser
from aisle.lexer.impl.lexer import Lexer
from aisle.parser.impl.parser import Parser


@pytest.mark.parametrize(
    "src",
    [
        "",
        '"A comment located before project"',
        "scope containers Should Not Be Here"
    ]
)
def test_no_project_def(src):
    """Test that anything declared before project will fail."""
    tokens = Lexer(src).scan()
    nodes = Parser(src, tokens).parse()
    with pytest.raises(NoProjectDefinedError):
        Analyser(nodes).analyse()


@pytest.mark.parametrize(
    "src",
    [
        "scope project My Project\n"
        "scope context Some Other Project",

        "scope project Case Sensitive\n"
        "scope legend case sensitive"
    ]
)
def test_wrong_scope_name(src):
    """Test that scope that doesn't match project's name will fail."""
    tokens = Lexer(src).scan()
    nodes = Parser(src, tokens).parse()
    with pytest.raises(UnmatchedProjectAndScopeNameError):
        Analyser(nodes).analyse()


@pytest.mark.parametrize(
    "src",
    [
        "scope project My Project\n"
        "scope project Some Other Project",

        "scope project Case Sensitive\n"
        "scope project case sensitive"
    ]
)
def test_duplicate_project(src):
    """Test that declaring two projects at once will fail."""
    tokens = Lexer(src).scan()
    nodes = Parser(src, tokens).parse()
    with pytest.raises(DuplicateProjectDefinitionError):
        Analyser(nodes).analyse()
