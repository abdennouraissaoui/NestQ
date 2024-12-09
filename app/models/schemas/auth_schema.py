from pydantic import BaseModel, Field


class TokenResponseSchema(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (bearer)")
    expires_at: int = Field(..., description="Token expiration timestamp")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")


class PasswordResetRequestSchema(BaseModel):
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Email address of the user requesting password reset",
        example="john.doe@example.com",
    )


class PasswordResetSchema(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, description="New password for the user account"
    )
