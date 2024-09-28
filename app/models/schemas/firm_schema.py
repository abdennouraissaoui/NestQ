from typing import List, Optional
from pydantic import BaseModel, Field
from .user_schema import UserDisplaySchema


class FirmBaseSchema(BaseModel):
    name: str = Field(..., description="Name of the firm")
    description: Optional[str] = Field(None, description="Description of the firm")


class FirmCreateSchema(FirmBaseSchema):
    pass


class FirmUpdateSchema(FirmBaseSchema):
    pass


class FirmDisplaySchema(FirmBaseSchema):
    id: int = Field(..., description="Unique identifier for the firm")
    users: List[UserDisplaySchema] = Field(
        ..., description="List of users associated with the firm"
    )

    class Config:
        from_attributes = True
