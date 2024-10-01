from typing import List, Optional
from pydantic import BaseModel, Field
from .user_schema import UserDisplaySchema


class FirmBaseSchema(BaseModel):
    name: str = Field(..., description="Name of the firm", example="Tech Corp")
    description: Optional[str] = Field(
        None,
        description="Description of the firm",
        example="A leading tech company",
    )


class FirmCreateSchema(FirmBaseSchema):
    pass


class FirmUpdateSchema(FirmBaseSchema):
    pass


class FirmDisplaySchema(FirmBaseSchema):
    id: int = Field(..., description="Unique identifier for the firm", example=1)
    users: List[UserDisplaySchema] = Field(
        ...,
        description="List of users associated with the firm",
        example=[{"id": 1, "first_name": "John", "last_name": "Doe"}],
    )

    class Config:
        from_attributes = True


class FirmDetailDisplaySchema(FirmDisplaySchema):
    created_at: int = Field(
        ..., description="Timestamp when the firm was created", example=1622547800
    )
    updated_at: int = Field(
        ...,
        description="Timestamp when the firm was last updated",
        example=1622547900,
    )
