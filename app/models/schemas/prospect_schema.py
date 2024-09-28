from typing import List, Optional
from pydantic import BaseModel, Field
from .account_schema import AccountCreateSchema, AccountDisplaySchema
from .address_schema import AddressCreateSchema, AddressDisplaySchema


class ProspectBaseSchema(BaseModel):
    first_name: Optional[str] = Field(description="First name of the prospect")
    last_name: Optional[str] = Field(description="Last name of the prospect")


class ProspectCreateSchema(ProspectBaseSchema):
    addresses: List[AddressCreateSchema] = Field(
        description="List of addresses for the prospect"
    )
    accounts: List[AccountCreateSchema] = Field(
        description="List of accounts for the prospect"
    )


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
    documents: List[str] = Field(
        description="List of document filenames associated with the prospect",
        example=["doc1.pdf", "doc2.pdf"],
    )
    addresses: List[AddressDisplaySchema] = Field(
        description="List of addresses for the prospect"
    )
    accounts: List[AccountDisplaySchema] = Field(
        description="List of accounts for the prospect"
    )


class ProspectUpdateSchema(ProspectBaseSchema):
    pass
