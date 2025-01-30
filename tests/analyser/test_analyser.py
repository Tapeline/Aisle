from pathlib import Path

import pytest

from aisle.analyser.analyser import Analyser
from aisle.analyser.entities.containers import ServiceEntity
from aisle.analyser.entities.context import ActorEntity, SystemEntity
from aisle.analyser.entities.deployment import DeploymentEntity, ServiceDeployment
from aisle.analyser.entities.links import Link
from aisle.analyser.entities.project import Project
from aisle.analyser.entities.styling import LegendStyling, StylingAttributes
from aisle.lexer.lexer import Lexer
from aisle.parser.nodes.legend import LegendSelectorType, LegendSelector
from aisle.parser.nodes.links import LinkType
from aisle.parser.parser import Parser


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        (
            Path("tests/fixtures/test_1_a.aisle").read_text(),
            Project(
                name="Blogging app",
                description="A simple blogging app architecture",
                namespace={
                    "Admin": ActorEntity(
                        name="Admin",
                        description="Blog moderator",
                        links=[
                            Link(
                                type=LinkType.OUTGOING,
                                to="Blogging System",
                                over=None,
                                description="Uses",
                            ),
                            Link(
                                type=LinkType.OUTGOING,
                                to="Metrics System",
                                over=None,
                                description="Reviews post metrics",
                            ),
                        ],
                        tags=[],
                    ),
                    "Backend Service": ServiceEntity(
                        name="Backend Service",
                        description=(
                                "Provides API\n"
                                "Maybe split into microservices later"
                        ),
                        system="Blogging System",
                        tech="Litestar, sqlalchemy",
                        links=[
                            Link(
                                type=LinkType.OUTGOING,
                                to="Metrics Service",
                                over="HTTP",
                                description=(
                                        "Send metrics info on each request"
                                ),
                            ),
                            Link(
                                type=LinkType.OUTGOING,
                                to="DB Service",
                                over=None,
                                description="Stores info",
                            ),
                        ],
                        tags=[],
                    ),
                    "Blogging System": SystemEntity(
                        name="Blogging System",
                        description="Stores and manages blogs",
                        links=[
                            Link(
                                type=LinkType.OUTGOING,
                                to="Metrics System",
                                over=None,
                                description="",
                            )
                        ],
                        tags=[],
                    ),
                    "DB Service": ServiceEntity(
                        name="DB Service",
                        description="",
                        system="Blogging System",
                        tech="Postgres",
                        links=[],
                        tags=[],
                    ),
                    "Frontend Service": ServiceEntity(
                        name="Frontend Service",
                        description="UI",
                        system="Blogging System",
                        tech="Vite+Vue",
                        links=[
                            Link(
                                type=LinkType.OUTGOING,
                                to="Backend Service",
                                over="HTTP",
                                description="Send API requests",
                            ),
                            Link(
                                type=LinkType.INCOMING,
                                to="User",
                                over=None,
                                description="",
                            ),
                            Link(
                                type=LinkType.INCOMING,
                                to="Admin",
                                over=None,
                                description="",
                            )
                        ],
                        tags=[],
                    ),
                    "Metrics Service": ServiceEntity(
                        name="Metrics Service",
                        description="",
                        system="Metrics System",
                        tech=None,
                        links=[],
                        tags=[],
                        is_external=True
                    ),
                    "Metrics System": SystemEntity(
                        name="Metrics System",
                        description=(
                                "Collects site metrics\n"
                                "We will use Yandex Metrics"
                        ),
                        links=[],
                        tags=[],
                        is_external=True
                    ),
                    "Provided Metrics": DeploymentEntity(
                        name="Provided Metrics",
                        description="Metrics Service is already provided",
                        deploys=[
                            ServiceDeployment(
                                service_name="Metrics Service",
                                deploy_as="Cloud provider"
                            )
                        ],
                        tags=["Yandex"],
                        inner_entities=[],
                        is_external=True
                    ),
                    "User": ActorEntity(
                        name="User",
                        description=(
                                "Uses blogging app. Reads and creates posts"
                        ),
                        links=[
                            Link(
                                type=LinkType.OUTGOING,
                                to="Blogging System",
                                over=None,
                                description="Uses",
                            )
                        ],
                        tags=[],
                    ),
                    "VPS Deployment": DeploymentEntity(
                        name="VPS Deployment",
                        description="Docker containers with Docker compose",
                        deploys=[],
                        tags=[],
                        inner_entities=[
                            DeploymentEntity(
                                name="Docker compose",
                                description="",
                                deploys=[
                                    ServiceDeployment(
                                        service_name="Frontend Service",
                                        deploy_as="Docker container"
                                    ),
                                    ServiceDeployment(
                                        service_name="Backend Service",
                                        deploy_as="Docker container"
                                    ),
                                    ServiceDeployment(
                                        service_name="DB Service",
                                        deploy_as="Docker container"
                                    ),
                                ],
                                inner_entities=[],
                                tags=["docker_compose"]
                            )
                        ]
                    ),
                },
                styling=[
                    LegendStyling(
                        selector=LegendSelector(
                            type=LegendSelectorType.CONTAINS_REGEX,
                            selector="Docker"
                        ),
                        attrs=StylingAttributes(bg="#aaaaff", fg=None),
                        description="Docker container deployment",
                    ),
                    LegendStyling(
                        selector=LegendSelector(
                            type=LegendSelectorType.HAS_TAG,
                            selector="Yandex"
                        ),
                        attrs=StylingAttributes(bg="#777700", fg=None),
                        description="",
                    ),
                    LegendStyling(
                        selector=LegendSelector(
                            type=LegendSelectorType.MATCHES_REGEX,
                            selector="VPS Deployment"
                        ),
                        attrs=StylingAttributes(bg="#cccccc", fg=None),
                        description="",
                    ),
                    LegendStyling(
                        selector=LegendSelector(
                            type=LegendSelectorType.ENTITY_TYPE,
                            selector="system"
                        ),
                        attrs=StylingAttributes(bg=None, fg=None),
                        description="",
                    ),
                ],
                comments=["This is a comment"],
            )
        )
    ]
)
def test_analyser(src, expected):
    tokens = Lexer(src).scan()
    nodes = Parser(src, tokens).parse()
    project = Analyser(nodes).analyse()
    assert project == expected
