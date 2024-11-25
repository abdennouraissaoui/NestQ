from pydantic import BaseModel, Field


class TokenResponseSchema(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (bearer)")
    expires_at: int = Field(..., description="Token expiration timestamp")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
