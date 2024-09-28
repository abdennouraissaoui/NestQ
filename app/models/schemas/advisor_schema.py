from typing import List
from pydantic import BaseModel, Field
from .prospect_schema import ProspectDisplaySchema


class AdvisorBaseSchema(BaseModel):
    first_name: str = Field(description="First name of the advisor", example="Jane")
    last_name: str = Field(description="Last name of the advisor", example="Doe")


class AdvisorCreateSchema(AdvisorBaseSchema):
    pass


class AdvisorDisplaySchema(AdvisorBaseSchema):
    id: int = Field(description="ID of the advisor", example=1)
    created_at: int = Field(
        description="Unix timestamp when the advisor was created", example=1622547800
    )

    class Config:
        from_attributes = True


class AdvisorDetailDisplaySchema(AdvisorDisplaySchema):
    prospects: List[ProspectDisplaySchema] = Field(
        description="List of prospects associated with the advisor"
    )


class AdvisorUpdateSchema(AdvisorBaseSchema):
    pass
