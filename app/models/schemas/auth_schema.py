from pydantic import BaseModel, Field


class TokenResponseSchema(BaseModel):
    access_token: str = Field(..., description="The access token")
    token_type: str = Field(..., description="The type of the token")
    expires_at: int = Field(..., description="The expiration time of the access token as a Unix epoch timestamp")
