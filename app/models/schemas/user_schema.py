from pydantic import BaseModel, Field
from app.models.enums import Role


class UserBaseSchema(BaseModel):
    firm_id: int = Field(
        ...,
        examples=[1],
        description="ID of the firm the user belongs to",
        example=1,
    )
    role: Role = Field(
        ..., description="Role of the user in the system", example=Role.ADVISOR
    )
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["test@example.com"],
        description="Email address of the user",
    )
    first_name: str = Field(
        ..., min_length=2, examples=["John"], description="First name of the user"
    )
    last_name: str = Field(
        ..., min_length=2, examples=["Doe"], description="Last name of the user"
    )
    phone_number: str = Field(
        ..., examples=["6479700630"], description="Phone number of the user"
    )


class UserCreateSchema(UserBaseSchema):
    password: str = Field(
        ..., examples=["password"], description="Password for the user account"
    )


class UserUpdateSchema(BaseModel):
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["test@example.com"],
        description="Email address of the user",
    )
    first_name: str = Field(
        ..., min_length=2, examples=["John"], description="First name of the user"
    )
    last_name: str = Field(
        ..., min_length=2, examples=["Doe"], description="Last name of the user"
    )
    phone_number: str = Field(
        ..., examples=["6479700630"], description="Phone number of the user"
    )


class UserDisplaySchema(UserBaseSchema):
    id: int = Field(description="Unique identifier for the user", example=1)

    class Config:
        from_attributes = True


class UserDetailDisplaySchema(UserDisplaySchema):
    created_at: int = Field(
        description="Timestamp when the user was created", example=1622547800
    )
    updated_at: int = Field(
        ..., description="Timestamp when the user was last updated"
    )
