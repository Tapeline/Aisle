"""Contains lexer tests."""

import pytest

from aisle.analyser.exceptions import NoProjectDefinedException
from aisle.parser.nodes.text import TextNode


@pytest.mark.parametrize(
    ("src", "err", "expected"),
    [
        (
            "Comment",
            NoProjectDefinedException(node=TextNode(1, "Comment")),
            "Exception while analysing node Text(Comment)\n"
            "At line: 1\n"
            "1 |  Comment\n"
            "Found TextNode node, but no project was defined. "
            "Define a project first!"
        ),
    ],
)
def test_error_format(src, err, expected):
    """Test that analyzer errors are formatted correctly."""
    assert err.formatted_message(src) == expected
