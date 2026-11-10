"""Small validated input model for the starter's typing checks."""

from typing import Self

from pydantic import BaseModel, field_validator


class StarterConfig(BaseModel):
    """Demonstrate typed fields, validation, and dictionary input."""

    name: str
    enabled: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Normalize names and reject empty input."""
        name = value.strip()
        if not name:
            raise ValueError("name must not be blank")
        return name

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """Validate external dictionary input using pydantic."""
        return cls.model_validate(data)
