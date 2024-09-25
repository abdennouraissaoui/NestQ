from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from utils.auth import get_current_user
from app.models.database import address_db
from app.models.database.schema import User
from app.models.schemas import AddressDisplay, AddressPut
from utils.db_connection_manager import get_db

router = APIRouter(
    prefix="/address",
    tags=["Address"],
)


@router.post(
    "/",
    response_model=AddressDisplay,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new address",
    description="Create a new address for a prospect.",
    response_description="The created address.",
)
def create_address(
    address: AddressPut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not address_db.is_advisor_prospect(
        db, current_user.advisor.id, address.prospect_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create an address for this prospect",
        )
    return address_db.create_address(db, address)


@router.get(
    "/prospect/{prospect_id}",
    response_model=List[AddressDisplay],
    summary="Get addresses by prospect",
    description="Retrieve all addresses for a specific prospect.",
    response_description="A list of addresses associated with the prospect.",
)
def get_addresses_by_prospect(
    prospect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not address_db.is_advisor_prospect(db, current_user.advisor.id, prospect_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access addresses for this prospect",
        )
    return address_db.get_addresses_by_prospect(db, prospect_id)


@router.get(
    "/{address_id}",
    response_model=AddressDisplay,
    summary="Get an address by ID",
    description="Retrieve a specific address by its ID.",
    response_description="The requested address details.",
)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = address_db.get_address_by_id(db, address_id)
    if not address_db.is_advisor_prospect(
        db, current_user.advisor.id, address.prospect_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this address",
        )
    return address


@router.put(
    "/{address_id}",
    response_model=AddressDisplay,
    summary="Update an address",
    description="Update an existing address.",
    response_description="The updated address details.",
)
def update_address(
    address_id: int,
    address_update: AddressPut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = address_db.get_address_by_id(db, address_id)
    if not address_db.is_advisor_prospect(
        db, current_user.advisor.id, address.prospect_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this address",
        )
    return address_db.update_address(db, address_id, address_update)


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an address",
    description="Delete an existing address.",
    response_description="No content, address successfully deleted.",
)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = address_db.get_address_by_id(db, address_id)
    if not address_db.is_advisor_prospect(
        db, current_user.advisor.id, address.prospect_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this address",
        )
    address_db.delete_address(db, address_id)
