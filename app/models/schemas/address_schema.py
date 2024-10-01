from typing import Optional
from pydantic import BaseModel, Field


class AddressBaseSchema(BaseModel):
    unit_number: Optional[str] = Field(
        None, description="Unit number of the address", example="Suite 200"
    )
    street_number: str = Field(
        ..., description="Street number of the address", example="123"
    )
    street_name: str = Field(
        ..., description="Street name of the address", example="Main Street"
    )
    city: str = Field(..., description="City of the address", example="Toronto")
    state: str = Field(
        ..., description="State or province of the address", example="Ontario"
    )
    postal_code: str = Field(
        ..., description="Postal code of the address", example="M5V 2T6"
    )
    country: str = Field(
        ..., description="Country of the address", example="Canada"
    )


class AddressCreateSchema(AddressBaseSchema):
    prospect_id: int = Field(
        ...,
        description="ID of the prospect associated with this address",
        example=1,
    )


class AddressDisplaySchema(AddressBaseSchema):
    id: int = Field(
        ..., description="Unique identifier for the address", example=1
    )
    created_at: int = Field(
        ...,
        description="Timestamp when the address was created",
        example=1622547800,
    )
    updated_at: int = Field(
        ...,
        description="Timestamp when the address was last updated",
        example=1622547900,
    )

    class Config:
        from_attributes = True


class AddressUpdateSchema(AddressBaseSchema):
    pass


class AddressDetailDisplaySchema(AddressDisplaySchema):
    created_at: int = Field(
        ..., description="Timestamp when the address was created"
    )
    updated_at: int = Field(
        ..., description="Timestamp when the address was last updated"
    )
