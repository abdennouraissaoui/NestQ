from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    access_token: str = Field(
        ...,
        description="The access token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    token_type: str = Field(
        ..., description="The type of the token", example="Bearer"
    )


class TokenResponseSchema(TokenSchema):
    class Config:
        from_attributes = True
