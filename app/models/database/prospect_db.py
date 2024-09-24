from sqlalchemy.orm import Session
from app.models.database.schema import Prospect
from app.models.schemas import Prospect as ProspectSchema


def create_prospect(db: Session, prospect: ProspectSchema):
    db_prospect = Prospect(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        advisor_id=prospect.advisor_id,
    )
    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect


def get_prospects_by_advisor(db: Session, advisor_id: int):
    return db.query(Prospect).filter(Prospect.advisor_id == advisor_id).all()


def get_prospect(db: Session, prospect_id: int):
    return db.query(Prospect).filter(Prospect.id == prospect_id).first()


def update_prospect(
    db: Session, db_prospect: Prospect, prospect_update: ProspectSchema
):
    for key, value in prospect_update.dict(exclude_unset=True).items():
        setattr(db_prospect, key, value)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect


def delete_prospect(db: Session, prospect_id: int):
    db_prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if db_prospect:
        db.delete(db_prospect)
        db.commit()
    return db_prospect
