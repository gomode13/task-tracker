from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_done: bool | None = None

    @model_validator(mode="after")
    def check_any_field_provided(self) -> Self:
        if not self.model_fields_set:
            raise PydanticCustomError("no_fields_provided", "At least one field must be provided")
        return self


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    is_done: bool
