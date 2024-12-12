from sqlalchemy.orm import Session
from app.models.database.orm_models import Advisor, Prospect, Scan
from app.models.schemas.scan_schema import (
    ScanCreateSchema,
    ScanProcessorUpdateSchema,
)
from app.utils.db_connection_manager import SessionLocal
from app.services.statement_extractor import FinancialStatementProcessor
from app.models.schemas.prospect_schema import ProspectCreateSchema
from app.models.database.prospect_db import create_prospect
from app.models.database.account_db import create_account
from app.models.schemas.scan_schema import ScanStatus


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
    return db.query(Scan).filter(Scan.id == scan_id).first()


async def process_scan(scan_id: int, advisor_id: int, document_base64):
    print(f"Processing scan {scan_id} for advisor {advisor_id}")
    with SessionLocal() as db:
        try:
            print(f"Scanning document with id {scan_id}")
            statement_processor = FinancialStatementProcessor()
            update, extracted_data = await statement_processor.process_scan(
                document_base64
            )
            print(f"Extracted data: {scan_id}")

            new_prospect = create_prospect(
                db,
                ProspectCreateSchema(
                    first_name=extracted_data.investor_first_name,
                    last_name=extracted_data.investor_last_name,
                ),
                advisor_id,
            )
            update.prospect_id = new_prospect.id
            update_scan(db, scan_id, update)

            for account_create in extracted_data.accounts:
                create_account(db, account_create, new_prospect.id)

            db.commit()
        except Exception as e:
            db.rollback()
            error_update = ScanProcessorUpdateSchema(
                status=ScanStatus.ERROR, error_message=str(e)
            )
            update_scan(db, scan_id, error_update)
            raise e
