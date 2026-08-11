from typing import Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from pydantic_core import PydanticCustomError


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    password_repeat: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise PydanticCustomError("passwords_mismatch", "Passwords do not match")
        return self


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str
