from sqlalchemy.orm import Session, joinedload


from app.models.database.orm_models import Advisor, Prospect, Scan


from app.models.schemas.scan_schema import (
    ScanCreateSchema,
    ScanProcessorUpdateSchema,
)


def create_scan(db: Session, scan: ScanCreateSchema) -> Scan:
    db_scan = Scan(**scan.dict())
    db.add(db_scan)
    db.commit()

    db.refresh(db_scan)
    return db_scan


def get_scan(db: Session, scan_id: int) -> Scan:
    return db.query(Scan).filter(Scan.id == scan_id).first()


def update_scan(
    db: Session, scan_id: int, scan_update: ScanProcessorUpdateSchema
) -> Scan:
    db_scan = get_scan(db, scan_id)
    if db_scan:
        update_data = scan_update.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_scan, key, value)
        db.commit()

        db.refresh(db_scan)
    return db_scan


def delete_scan(db: Session, scan_id: int) -> bool:
    db_scan = get_scan(db, scan_id)
    if db_scan:
        db.delete(db_scan)
        db.commit()

        return True

    return False


def list_scans(db: Session, advisor_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Scan)
        .join(Scan.prospect)
        .join(Prospect.advisor)
        .filter(Advisor.id == advisor_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_scans_by_prospect_id(db: Session, advisor_id: int, prospect_id: int):
    return (
        db.query(Scan)
        .join(Scan.prospect)
        .join(Prospect.advisor)
        .filter(Prospect.id == prospect_id, Advisor.id == advisor_id)
        .all()
    )


def get_scan_with_relations(db: Session, scan_id: int) -> Scan:
    return db.query(Scan).options(
        joinedload(Scan.prospect),
        joinedload(Scan.prospect).joinedload(Prospect.accounts)
    ).filter(Scan.id == scan_id).first()
