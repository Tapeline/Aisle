"""Contains lexer tests."""
from pathlib import Path
from typing import Final

import pytest

from aisle.lexer.lexer import Lexer
from aisle.lexer.tokens import Token, TokenType


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        (
            ":=()[]",
            [
                "COLON:",
                "ASSIGN=",
                "LPAR(",
                "RPAR)",
                "LBRACKET[",
                "RBRACKET]",
            ],
        ),
        (
            "This_is_a_text",
            ["TEXTThis_is_a_text"],
        ),
        (
            "scope",
            ["KEYWORDscope"],
        ),
        (
            "---<----><->",
            [
                "ARROW_NO_DIR---",
                "ARROW_L<--",
                "ARROW_R-->",
                "ARROW_BI_DIR<->",
            ],
        ),
        (
            "\n\r\n\t    ",  # also check that CRLF is processed correctly
            [
                "NEWLINE\n",
                "NEWLINE\n",
                "INDENT\t",
                "INDENT    ",
            ],
        ),
    ],
)
def test_simple_tokens(src, expected):
    """Test that simple tokens are processed correctly."""
    lexer = Lexer(src)
    tokens = lexer.scan()
    assert list(map(str, tokens)) == expected


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        (
            '"String"',
            ["TEXTString"],
        ),
        (
            '"String""Followed by a string"',
            [
                "TEXTString",
                "TEXTFollowed by a string",
            ],
        ),
        (
            '"Escape \\n \\r \\t \\f \\u0462 \\\\ \\""',
            ['TEXTEscape \n \r \t \f \u0462 \\ "'],
        ),
    ],
)
def test_strings(src, expected):
    """Test that strings are processed correctly."""
    lexer = Lexer(src)
    tokens = lexer.scan()
    assert list(map(str, tokens)) == expected


code_all_quoted: Final[str] = (
    'service Backend:\n'
    '    "Provides API\\nMaybe split into microservices later"\n'
    '    tech = "Litestar, sqlalchemy, \\nfaststream"\n'
    '    links:\n'
    '        --> "Anti-fraud Service" over "HTTP"'
)
code_unquoted: Final[str] = (
    "service Backend:\n"
    "    Provides API\\nMaybe split into microservices later\n"
    "    tech = Litestar, sqlalchemy, \\nfaststream\n"
    "    links:\n"
    "        --> Anti-fraud Service over HTTP"
)
code_unquoted_multiline: Final[str] = (
    "service Backend:\n"
    "    Provides API\n"
    "    Maybe split into microservices later\n"
    "    tech = Litestar, sqlalchemy, \n"
    "           faststream\n"
    "    links:\n"
    "        --> Anti-fraud Service over HTTP"
)
expected_tokens: Final[list[str]] = [
    "KEYWORDservice",
    "TEXTBackend",
    "COLON:",
    "NEWLINE\n",
    "INDENT    ",
    "TEXTProvides API\nMaybe split into microservices later",
    "NEWLINE\n",
    "INDENT    ",
    "KEYWORDtech",
    "ASSIGN=",
    "TEXTLitestar, sqlalchemy, \nfaststream",
    "NEWLINE\n",
    "INDENT    ",
    "KEYWORDlinks",
    "COLON:",
    "NEWLINE\n",
    "INDENT    ",
    "INDENT    ",
    "ARROW_R-->",
    "TEXTAnti-fraud Service",
    "KEYWORDover",
    "TEXTHTTP",
]


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        (code_all_quoted, expected_tokens),
        (code_unquoted, expected_tokens),
        (code_unquoted_multiline, expected_tokens),
    ],
)
def test_complex_code(src, expected):
    """Test that a complex code is lexed correctly."""
    lexer = Lexer(src)
    tokens = lexer.scan()
    assert list(map(str, tokens)) == expected


def test_multiline_edge_case():
    """Cover """
    src = (
        "scope project Test\n"
        "scope context Test\n"
        "system TestSystem:\n"
        "    description\n"
        "    tech = Tech\n"
        "    links:\n"
        "        --> Test\n"
    )
    tokens = Lexer(src).scan()
    expected = [
        "KEYWORDscope",
        "KEYWORDproject",
        "TEXTTest",
        "NEWLINE\n",
        "KEYWORDscope",
        "KEYWORDcontext",
        "TEXTTest",
        "NEWLINE\n",
        "KEYWORDsystem",
        "TEXTTestSystem",
        "COLON:",
        "NEWLINE\n",
        "INDENT    ",
        "TEXTdescription",
        "NEWLINE\n",
        "INDENT    ",
        "KEYWORDtech",
        "ASSIGN=",
        "TEXTTech",
        "NEWLINE\n",
        "INDENT    ",
        "KEYWORDlinks",
        "COLON:",
        "NEWLINE\n",
        "INDENT    ",
        "INDENT    ",
        "ARROW_R-->",
        "TEXTTest",
        "NEWLINE\n"
    ]
    assert list(map(str, tokens)) == expected


def test_with_real_file(snapshot):
    """Test that real project declaration is lexed correctly."""
    with Path("./tests/fixtures/test_1.aisle").open("r") as src_file:
        src = src_file.read()
    lexer = Lexer(src)
    tokens = lexer.scan()
    tokens_str = "\n".join(map(str, tokens))
    assert tokens_str == snapshot


def test_token_human_readable_repr():
    token = Token(TokenType.KEYWORD, "system", 2)
    expected = "2\t| KEYWORD       system"
    assert token.human_readable_repr == expected
