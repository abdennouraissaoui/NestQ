from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.database.orm_models import Holding
from app.models.schemas.holding_schema import (
    HoldingCreateSchema,
    HoldingUpdateSchema,
)
from app.models.schemas.user_schema import UserBaseSchema
from app.models.database.prospect_db import get_prospect
from app.models.database.scan_db import get_scan


def create_holding(
    db: Session, holding: HoldingCreateSchema, current_user: UserBaseSchema
):
    prospect = get_prospect(db, holding.prospect_id)
    if prospect.advisor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the advisor of the prospect can create holdings",
        )

    db_holding = Holding(**holding.dict())
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    return db_holding


def get_holding_by_id(db: Session, holding_id: int, current_user: UserBaseSchema):
    holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    prospect = get_prospect(db, holding.prospect_id)
    if prospect.advisor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return holding


def update_holding(
    db: Session,
    holding_id: int,
    holding: HoldingUpdateSchema,
    current_user: UserBaseSchema,
):
    db_holding = get_holding_by_id(db, holding_id, current_user)

    for key, value in holding.dict(exclude_unset=True).items():
        setattr(db_holding, key, value)

    db.commit()
    db.refresh(db_holding)
    return db_holding


def delete_holding(db: Session, holding_id: int, current_user: UserBaseSchema):
    db_holding = get_holding_by_id(db, holding_id, current_user)
    db.delete(db_holding)
    db.commit()


def get_holdings_by_scan(db: Session, scan_id: int, current_user: UserBaseSchema):
    scan = get_scan(db, scan_id)
    if scan.advisor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(Holding).filter(Holding.scan_id == scan_id).all()


def get_holdings_by_prospect(
    db: Session, prospect_id: int, current_user: UserBaseSchema
):
    prospect = get_prospect(db, prospect_id)
    if prospect.advisor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(Holding).filter(Holding.prospect_id == prospect_id).all()
