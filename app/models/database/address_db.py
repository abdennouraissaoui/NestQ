from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.database.orm_models import Address, Prospect
from app.models.schemas.address_schema import AddressCreateSchema, AddressUpdateSchema

address_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Address not found",
)

prospect_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Prospect not found",
)


def _get_address_or_raise(db: Session, address_id: int) -> Address:
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise address_not_found_exception
    return address


def is_advisor_prospect(db: Session, advisor_id: int, prospect_id: int) -> bool:
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not prospect:
        raise prospect_not_found_exception
    return prospect.advisor_id == advisor_id


def create_address(db: Session, address: AddressCreateSchema) -> Address:
    db_address = Address(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def get_addresses_by_prospect(db: Session, prospect_id: int) -> List[Address]:
    return db.query(Address).filter(Address.prospect_id == prospect_id).all()


def get_address_by_id(db: Session, address_id: int) -> Address:
    return _get_address_or_raise(db, address_id)


def update_address(
    db: Session, address_id: int, address_update: AddressUpdateSchema
) -> Address:
    db_address = _get_address_or_raise(db, address_id)
    for field, value in address_update.dict(exclude_unset=True).items():
        setattr(db_address, field, value)
    db.commit()
    db.refresh(db_address)
    return db_address


def delete_address(db: Session, address_id: int):
    db_address = _get_address_or_raise(db, address_id)
    db.delete(db_address)
    db.commit()
