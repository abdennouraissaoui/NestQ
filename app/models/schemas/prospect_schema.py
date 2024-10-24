from typing import List, Optional
from pydantic import BaseModel, Field
from .address_schema import AddressDisplaySchema
from .account_schema import AccountDisplaySchema


class ProspectBaseSchema(BaseModel):
    first_name: Optional[str] = Field(
        description="First name of the prospect", example="John"
    )
    last_name: Optional[str] = Field(
        description="Last name of the prospect", example="Doe"
    )


class ProspectCreateSchema(ProspectBaseSchema):
    pass


class ProspectDisplaySchema(ProspectBaseSchema):
    id: int = Field(description="ID of the prospect", example=1)
    created_at: int = Field(
        description="Timestamp when the prospect was created", example=1622547800
    )
    updated_at: int = Field(
        description="Timestamp when the prospect was last updated",
        example=1622547900,
    )

    class Config:
        from_attributes = True


class ProspectDetailDisplaySchema(ProspectDisplaySchema):
    scans: List[str] = Field(
        description="List of document filenames associated with the prospect",
        example=["doc1.pdf", "doc2.pdf"],
    )
    addresses: List[AddressDisplaySchema] = Field(
        description="List of addresses for the prospect",
        example=[
            {
                "street_number": "123",
                "street_name": "Main St",
                "city": "Toronto",
                "state": "ON",
                "postal_code": "M5V 2T6",
                "country": "Canada",
            }
        ],
    )
    accounts: List[AccountDisplaySchema] = Field(
        description="List of accounts for the prospect",
        example=[
            {"account_id": "ACC123", "account_type": "Savings", "currency": "CAD"}
        ],
    )


class ProspectUpdateSchema(ProspectBaseSchema):
    pass
