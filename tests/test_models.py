"""Preserve the starter model's validation and normalization behavior."""

import pytest
from pydantic import ValidationError

from python_starter.models import StarterConfig


def test_valid_input_and_default() -> None:
    config = StarterConfig(name="starter")

    assert config.name == "starter"
    assert config.enabled is True


def test_dictionary_input_normalizes_name() -> None:
    config = StarterConfig.from_dict({"name": "  starter\t", "enabled": False})

    assert config.name == "starter"
    assert config.enabled is False


@pytest.mark.parametrize("name", ["", " ", "\t\n"])
def test_blank_name_is_rejected(name: str) -> None:
    with pytest.raises(ValidationError, match="name must not be blank"):
        StarterConfig(name=name)


@pytest.mark.parametrize(
    ("data", "field", "error_type"),
    [
        ({}, "name", "missing"),
        ({"name": 42}, "name", "string_type"),
        ({"name": "starter", "enabled": "invalid"}, "enabled", "bool_parsing"),
    ],
)
def test_invalid_input_is_rejected(
    data: dict[str, object], field: str, error_type: str
) -> None:
    with pytest.raises(ValidationError) as raised:
        StarterConfig.from_dict(data)

    error = raised.value.errors()[0]
    assert error["loc"] == (field,)
    assert error["type"] == error_type


def test_round_trip() -> None:
    original = StarterConfig(name="starter", enabled=False)

    restored = StarterConfig.from_dict(original.model_dump())

    assert restored == original
    assert restored.model_dump() == {"name": "starter", "enabled": False}
