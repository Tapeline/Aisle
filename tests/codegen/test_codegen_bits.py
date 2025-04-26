import pytest

from aisle.analyser.entities.containers import ServiceEntity
from aisle.analyser.entities.context import SystemEntity
from aisle.codegen.impl.plantuml.plantuml import _get_node_type


@pytest.mark.parametrize(
    ("entity", "base", "expected"),
    [
        (
            SystemEntity("A", "", [], tags=["db"]),
            "System",
            "Db"
        ),
        (
            SystemEntity("A", "", [], tags=["database"]),
            "System",
            "Db"
        ),
        (
            SystemEntity("A", "", [], tags=["queue"]),
            "System",
            "Queue"
        ),
        (
            SystemEntity("A", "", [], tags=[]),
            "System",
            ""
        ),
        (
            ServiceEntity("A", "", None, None, [], tags=["db"]),
            "Container",
            "Db"
        ),
        (
            ServiceEntity("A", "", None, None, [], tags=["database"]),
            "Container",
            "Db"
        ),
        (
            ServiceEntity("A", "", None, None, [], tags=["queue"]),
            "Container",
            "Queue"
        ),
        (
            ServiceEntity("A", "", None, None, [], tags=[]),
            "Container",
            ""
        ),
    ]
)
def test_node_type_generation(entity, base, expected):
    node_t = _get_node_type(base, entity)
    assert node_t == base + expected
