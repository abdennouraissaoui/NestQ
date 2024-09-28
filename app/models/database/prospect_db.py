from sqlalchemy.orm import Session
from app.models.database.orm_models import Prospect
from app.models.schemas.prospect_schema import (
    ProspectCreateSchema,
    ProspectUpdateSchema,
)
from typing import List


def create_prospect(
    db: Session, prospect: ProspectCreateSchema, advisor_id: int
) -> Prospect:
    db_prospect = Prospect(**prospect.dict())
    db_prospect.advisor_id = advisor_id
    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect


def get_prospects_by_advisor(db: Session, advisor_id: int) -> List[Prospect]:
    prospects = db.query(Prospect).filter(Prospect.advisor_id == advisor_id).all()
    return prospects


def get_prospect(db: Session, prospect_id: int) -> Prospect:
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not prospect:
        return None
    return prospect


def update_prospect(
    db: Session, db_prospect: Prospect, prospect_update: ProspectUpdateSchema
) -> Prospect:
    for key, value in prospect_update.dict(exclude_unset=True).items():
        setattr(db_prospect, key, value)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect


def delete_prospect(db: Session, prospect_id: int) -> None:
    db_prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if db_prospect:
        db.delete(db_prospect)
        db.commit()
