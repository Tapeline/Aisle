"""Contains parser implementation and related things."""

from collections.abc import Callable, Sequence
from types import MappingProxyType

from aisle.lexer.tokens import Token, TokenType
from aisle.parser.exceptions import (
    UnexpectedEndException,
    UnexpectedKeywordTokenException,
    UnexpectedTokenException,
)
from aisle.parser.nodes.attribute import AttrNode
from aisle.parser.nodes.base import Node
from aisle.parser.nodes.entity import (
    DeployNode,
    EntityNode,
    EntityType,
    ProjectDefNode,
)
from aisle.parser.nodes.legend import (
    LegendDeclarationNode,
    LegendSelector,
    LegendSelectorType,
)
from aisle.parser.nodes.links import LinkCollectionNode, LinkNode, LinkType
from aisle.parser.nodes.scope import ScopeNode, ScopeType
from aisle.parser.nodes.text import TextNode

LINK_TOKEN_TO_TYPE = MappingProxyType({
    TokenType.ARROW_L: LinkType.INCOMING,
    TokenType.ARROW_R: LinkType.OUTGOING,
    TokenType.ARROW_BI_DIR: LinkType.BIDIRECTIONAL,
    TokenType.ARROW_NO_DIR: LinkType.NON_DIRECTED,
})


class Parser:
    """Parser impl."""

    def __init__(self, source_code: str, tokens: Sequence[Token]):
        """Create parser."""
        self._tokens = tokens
        self._src = source_code
        self._i = 0
        self._scope: ScopeType | None = None

    @property
    def _at_end(self) -> bool:
        """Check if there are no more tokens to parse."""
        return self._i >= len(self._tokens)

    def _next(self) -> Token | None:
        """Consume current token and advance to next."""
        if self._at_end:
            return None  # pragma: no cover
        self._i += 1
        return self._tokens[self._i - 1]

    @property
    def _peek(self) -> Token | None:
        """See current token without consuming it."""
        if self._at_end:
            return None  # pragma: no cover
        return self._tokens[self._i]

    @property
    def _previous(self) -> Token | None:
        """See previous token."""
        if self._i == 0:
            return None  # pragma: no cover
        return self._tokens[self._i - 1]

    def _match(
            self,
            expected_type: TokenType,
            extra_condition: Callable[[Token], bool] | None = None,
    ) -> Token | None:
        """Try to consume token that meets provided conditions."""
        if self._at_end:
            return None  # pragma: no cover
        if not extra_condition:
            extra_condition = lambda _: True  # noqa: E731
        if (
                self._peek.type == expected_type and
                extra_condition(self._peek)
        ):
            return self._next()
        return None

    def _error(self, exc_type, *args, **kwargs):
        """Raise an exception at current position."""
        raise exc_type(
            *args,
            **kwargs,
            source=self._src,
            line=self._tokens[min(len(self._tokens) - 1, self._i)].line,
        )

    def _require(
            self,
            expected_type: TokenType,
            *,
            extra_condition: Callable[[Token], bool] | None = None,
            message: str | None = None,
    ) -> Token:
        """Consume token meeting some conditions, or else raise exception."""
        token = self._match(expected_type, extra_condition)
        if token is None:
            self._error(
                UnexpectedTokenException,
                expected=[expected_type],
                got=self._peek,
                message=message,
            )
        return token

    def _match_kw(self, keyword: str) -> Token | None:
        """Try to consume specific keyword."""
        return self._match(
            TokenType.KEYWORD,
            lambda token: token.lexeme == keyword
        )

    def _match_any_type(
            self,
            *expected_types: TokenType,
    ) -> Token | None:
        """Try to consume token of one of provided types."""
        for expected_type in expected_types:
            token = self._match(expected_type)
            if token is not None:
                return token
        return None

    def _match_any_kw(self, *keywords: str) -> Token | None:
        """Try to consume keyword of one of provided."""
        for keyword in keywords:
            token = self._match_kw(keyword)
            if token is not None:
                return token
        return None

    def _require_kw(
            self,
            keyword: str,
            *,
            message: str | None = None,
    ) -> Token:
        """Consume a specific keyword, or else raise exception."""
        token = self._match(TokenType.KEYWORD, lambda t: t.lexeme == keyword)
        if token is None:
            self._error(
                UnexpectedKeywordTokenException,
                expected=[keyword],
                got=self._peek,
                message=message,
            )
        return token

    def _require_any_kw(
            self,
            *keywords: str,
            message: str | None = None,
    ) -> Token:
        """Consume a one of given keywords, or else raise exception."""
        token = self._match_any_kw(*keywords)
        if token is None:
            self._error(
                UnexpectedKeywordTokenException,
                expected=keywords,
                got=self._peek,
                message=message,
            )
        return token

    def _require_any_type(
            self,
            *types: TokenType,
            message: str | None = None,
    ) -> Token:
        """Consume a token of one of given types, or else raise exception."""
        token = self._match_any_type(*types)
        if token is None:
            self._error(
                UnexpectedTokenException,
                expected=types,
                got=self._peek,
                message=message,
            )
        return token

    def _match_n_indents(self, count: int) -> bool:
        """Try to consume exactly n indents and say if successful."""
        i = 0
        indents = 0
        while self._i + i < len(self._tokens):
            tok = self._tokens[self._i + i]
            if tok.type == TokenType.INDENT:
                indents += 1
            elif tok.type == TokenType.NEWLINE:
                indents = 0
            else:
                break
            i += 1
        if indents >= count:
            self._i += i
            return True
        return False

    def _matches_pattern(self, *pattern: TokenType) -> bool:
        """Check if there is a specific pattern of tokens ahead."""
        if self._i + len(pattern) >= len(self._tokens):
            return False
        for i in range(len(pattern)):
            if self._tokens[self._i + i].type != pattern[i]:
                return False
        return True

    def parse(self) -> Sequence[Node]:
        """Parse token stream."""
        stmts = []
        while not self._at_end:
            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)
        return stmts

    def _parse_statement(self) -> Node | None:  # type: ignore
        """Parse statement."""
        if self._match(TokenType.NEWLINE):
            return None
        if self._match_kw("scope"):
            scope_type = self._require_any_kw(
                "project",
                "containers",
                "context",
                "deployment",
                "legend",
            )
            if scope_type.lexeme == "project":
                return self._parse_project_def()
            name = self._require(TokenType.TEXT)
            self._scope = ScopeType(scope_type.lexeme)
            return ScopeNode(
                scope_type.line,
                self._scope,
                name.lexeme,
            )
        if self._match(TokenType.TEXT):
            return TextNode(self._previous.line, self._previous.lexeme)
        node: Node | None = None
        match self._scope:
            case ScopeType.CONTEXT:
                node = self._parse_context_entity()
            case ScopeType.CONTAINERS:
                node = self._parse_container_entity()
            case ScopeType.DEPLOYMENT:
                node = self._parse_deployment_entity()
            case ScopeType.LEGEND:
                node = self._parse_legend_declaration()
        if node:
            return node
        self._error(  # noqa: RET503 (no return -> exception is raised)
            UnexpectedTokenException,
            message=(
                "Expected scope, entity or a comment, "
                "but got '{got.type.name}': '{got.lexeme}'"
            ),
            got=self._peek,
        )

    def _parse_tags(self) -> Sequence[str]:
        """Parse entity tags."""
        tags = []
        while self._match(TokenType.LBRACKET):
            tag = self._require(TokenType.TEXT)
            self._require(TokenType.RBRACKET)
            tags.append(tag.lexeme)
        return tags

    def _parse_project_def(self) -> ProjectDefNode:
        """Parse project definition."""
        name = self._require(
            TokenType.TEXT,
            message="Expected project name, but got {got}",
        )
        if self._match(TokenType.COLON) is None:
            return ProjectDefNode(name.line, name.lexeme, [])
        description = []
        while self._match(TokenType.NEWLINE):
            if not self._match_n_indents(1):
                self._i -= 1
                break
            desc_token = self._require(
                TokenType.TEXT,
                message="Expected project description, but got {got}",
            )
            description.append(desc_token.lexeme)
        return ProjectDefNode(name.line, name.lexeme, description)

    def _parse_context_entity(self) -> EntityNode:
        """Parse context scope entity."""
        ext_modifier = self._match_kw("external")
        entity_type = self._require_any_kw("system", "actor")
        name = self._require(TokenType.TEXT)
        tags = self._parse_tags()
        colon = self._match(TokenType.COLON)
        body: Sequence[Node] = []
        if entity_type.lexeme == "actor":
            if colon:
                body = self._parse_actor_body()
            return EntityNode(
                entity_type.line,
                EntityType.ACTOR,
                name.lexeme,
                tags,
                body,
            )
        if entity_type.lexeme == "system":
            if colon:
                body = self._parse_system_or_container_body(is_system=True)
            return EntityNode(
                entity_type.line,
                EntityType.SYSTEM,
                name.lexeme,
                tags,
                body,
                is_external=ext_modifier is not None,
            )
        raise ValueError(  # pragma: no cover
            "Entity type did not match system nor actor"
        )

    def _parse_container_entity(self) -> EntityNode:
        """Parse container scope entity."""
        ext_modifier = self._match_kw("external")
        entity_type = self._require_kw("service")
        name = self._require(TokenType.TEXT)
        tags = self._parse_tags()
        body: Sequence[Node] = []
        if self._match(TokenType.COLON):
            body = self._parse_system_or_container_body(is_system=False)
        return EntityNode(
            entity_type.line,
            EntityType.SERVICE,
            name.lexeme,
            tags,
            body,
            is_external=ext_modifier is not None,
        )

    def _parse_deployment_entity(self) -> EntityNode:
        """Parse deployment scope entity."""
        ext_modifier = self._match_kw("external")
        entity_type = self._require_kw("deployment")
        name = self._require(TokenType.TEXT)
        tags = self._parse_tags()
        body: Sequence[Node] = []
        if self._match(TokenType.COLON):
            body = self._parse_deployment_body()
        return EntityNode(
            entity_type.line,
            EntityType.DEPLOYMENT,
            name.lexeme,
            tags,
            body,
            is_external=ext_modifier is not None,
        )

    def _parse_legend_declaration(
            self
    ) -> LegendDeclarationNode:
        """Parse legend styling rule."""
        selector = None
        token = None
        if self._match_any_kw("system", "service", "actor", "deployment"):
            token = self._previous
            selector = LegendSelector(
                type=LegendSelectorType.ENTITY_TYPE,
                selector=self._previous.lexeme,
            )
        else:
            token = self._require(
                TokenType.LBRACKET,
                message=(
                    "Expected legend selector "
                    "(entity type or bracket selector), "
                    "but got {got}"
                ),
            )
            if self._at_end:
                self._error(
                    UnexpectedEndException,
                    expected="legend tag",
                )
            selector_type = self._peek.lexeme
            if selector_type not in {"contains", "=", "tag"}:
                self._error(
                    UnexpectedTokenException,
                    expected=["contains", "tag", "="],
                    got=self._peek,
                )
            self._i += 1
            selector = LegendSelector(
                type=LegendSelectorType(selector_type),
                selector=self._require(TokenType.TEXT).lexeme,
            )
            self._require(TokenType.RBRACKET)
        self._require(TokenType.COLON)
        body = self._parse_legend_body()
        return LegendDeclarationNode(
            token.line,
            selector,
            body,
        )

    def _parse_actor_body(self) -> Sequence[Node]:
        """Parse body of actor entity."""
        nodes: list[Node] = []
        while self._match(TokenType.NEWLINE):
            if not self._match_n_indents(1):
                self._i -= 1
                break
            desc_token = self._match(TokenType.TEXT)
            if desc_token:
                nodes.append(TextNode(desc_token.line, desc_token.lexeme))
                continue
            if not self._at_end and self._peek.lexeme == "links":
                nodes.append(self._parse_links())
                continue
            self._error(
                UnexpectedTokenException,
                expected=["text description or links"],
                got=self._peek,
            )
        return nodes

    def _parse_links(self) -> LinkCollectionNode:
        """Parse link list."""
        token = self._require_kw("links")
        self._require(TokenType.COLON)
        links = []
        while self._match(TokenType.NEWLINE):
            if not self._match_n_indents(2):
                self._i -= 1
                break
            link_type = self._require_any_type(
                TokenType.ARROW_L,
                TokenType.ARROW_R,
                TokenType.ARROW_BI_DIR,
                TokenType.ARROW_NO_DIR,
            )
            link_to = self._require(TokenType.TEXT)
            link_over = None
            link_description: Sequence[str] = []
            if self._match_kw("over"):
                link_over = self._require(TokenType.TEXT).lexeme
            if self._match(TokenType.COLON):
                link_description = self._parse_link_description()
            link = LinkNode(
                link_type.line,
                LINK_TOKEN_TO_TYPE[link_type.type],
                link_to.lexeme,
                link_over,
                link_description,
            )
            links.append(link)
        return LinkCollectionNode(token.line, links)

    def _parse_link_description(self) -> Sequence[str]:
        """Parse description of a link."""
        strings = []
        while self._match(TokenType.NEWLINE):
            if not self._match_n_indents(3):
                self._i -= 1
                break
            token = self._require(TokenType.TEXT)
            strings.append(token.lexeme)
        return strings

    def _parse_system_or_container_body(
            self,
            is_system: bool  # noqa: FBT001 (bad but ok)
    ) -> Sequence[Node]:
        """Parse body of system or container entity."""
        nodes: list[Node] = []
        expected = ["text description", "links", "tech"]
        if not is_system:
            expected.append("system")
        while self._match(TokenType.NEWLINE):
            if not self._match_n_indents(1):
                self._i -= 1
                break
            desc_token = self._match(TokenType.TEXT)
            if desc_token:
                nodes.append(TextNode(desc_token.line, desc_token.lexeme))
                continue
            if not self._at_end and self._peek.lexeme == "links":
                nodes.append(self._parse_links())
                continue
            if not self._at_end and self._peek.lexeme == "tech":
                nodes.append(self._parse_attr())
                continue
            if not self._at_end and self._peek.lexeme == "system":
                if is_system:
                    self._error(
                        UnexpectedTokenException,
                        expected=expected,
                        got=self._peek,
                    )
                nodes.append(self._parse_attr())
                continue
            self._error(
                UnexpectedTokenException,
                expected=expected,
                got=self._peek,
            )
        return nodes

    def _parse_attr(self) -> AttrNode:
        """Parse attribute declaration."""
        attr = self._maybe_parse_attr()
        if attr is None:
            self._error(
                UnexpectedTokenException,
                expected=["attribute declaration"],
                got=self._peek,
            )
        return attr

    def _maybe_parse_attr(self) -> AttrNode | None:
        """Try to parse attribute declaration."""
        is_text_attr = self._matches_pattern(
            TokenType.TEXT,
            TokenType.ASSIGN,
            TokenType.TEXT,
        )
        is_keyword_attr = self._matches_pattern(
            TokenType.KEYWORD,
            TokenType.ASSIGN,
            TokenType.TEXT,
        )
        if not (is_text_attr or is_keyword_attr):
            return None
        name = self._next().lexeme
        token = self._require(TokenType.ASSIGN)
        value = self._require(TokenType.TEXT).lexeme
        return AttrNode(token.line, name, value)

    def _parse_deployment_body(self, indent_lvl: int = 1) -> Sequence[Node]:
        """Parse body of deployment configuration."""
        nodes: list[Node] = []
        while self._match(TokenType.NEWLINE):
            if not self._match_n_indents(indent_lvl):
                self._i -= 1
                break
            desc_token = self._match(TokenType.TEXT)
            tags = self._parse_tags()
            if desc_token:
                if self._match(TokenType.COLON):
                    nodes.append(EntityNode(
                        self._previous.line,
                        EntityType.DEPLOYMENT,
                        desc_token.lexeme,
                        tags,
                        self._parse_deployment_body(indent_lvl + 1)
                    ))
                else:
                    nodes.append(TextNode(desc_token.line, desc_token.lexeme))
                continue
            deploy_token = self._match_kw("deploy")
            if deploy_token:
                target = self._match(TokenType.TEXT).lexeme
                deploy_as = None
                if self._match(TokenType.ASSIGN):
                    deploy_as = self._require(TokenType.TEXT).lexeme
                nodes.append(DeployNode(deploy_token.line, target, deploy_as))
                continue
            self._error(
                UnexpectedTokenException,
                expected=["deploy, inner deploy or text description"],
                got=self._peek,
            )
        return nodes

    def _parse_legend_body(self) -> Sequence[Node]:
        """Parse body of legend styling rule."""
        nodes: list[Node] = []
        while self._match(TokenType.NEWLINE):
            if not self._match_n_indents(1):
                self._i -= 1
                break
            attr_node = self._maybe_parse_attr()
            if attr_node:
                nodes.append(attr_node)
                continue
            desc_token = self._match(TokenType.TEXT)
            if desc_token:
                nodes.append(TextNode(desc_token.line, desc_token.lexeme))
                continue
            self._error(
                UnexpectedTokenException,
                expected=["attribute or text description"],
                got=self._peek,
            )
        return nodes
