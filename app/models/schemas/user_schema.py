from pydantic import BaseModel, Field
from app.models.enums import Role


class UserBaseSchema(BaseModel):
    firm_id: int = Field(..., examples=[1])
    role: Role = Field(...)
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["test@example.com"],
    )
    first_name: str = Field(..., min_length=2, examples=["John"])
    last_name: str = Field(..., min_length=2, examples=["Doe"])
    phone_number: str = Field(..., examples=["6479700630"])


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., examples=["password"])


class UserUpdateSchema(BaseModel):
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["test@example.com"],
    )
    first_name: str = Field(..., min_length=2, examples=["John"])
    last_name: str = Field(..., min_length=2, examples=["Doe"])
    phone_number: str = Field(..., examples=["6479700630"])


class UserDisplaySchema(UserBaseSchema):
    id: int

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
