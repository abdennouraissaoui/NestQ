from sqlalchemy.orm import Session
from app.models.database.orm_models import Advisor, Prospect, Scan
from app.models.schemas.scan_schema import (
    ScanCreateSchema,
    ScanProcessorUpdateSchema,
    OcrResultSchema,
)
from app.utils.db_connection_manager import SessionLocal
from app.services.statement_extractor import FinancialStatementProcessor
from app.models.schemas.prospect_schema import ProspectCreateSchema
from app.models.database.prospect_db import create_prospect
from app.models.database.account_db import create_account
from app.models.database.orm_models import OcrResult
from sqlalchemy import select
from sqlalchemy.orm import contains_eager


def create_scan(db: Session, scan: ScanCreateSchema) -> Scan:
    db_scan = Scan(**scan.dict())
    db.add(db_scan)
    db.commit()

    db.refresh(db_scan)
    return db_scan


def get_scan(db: Session, scan_id: int) -> Scan:
    return db.query(Scan).filter(Scan.id == scan_id).first()


def get_scan_with_ocr_result(db: Session, scan_id: int) -> Scan:
    stmt = (
        select(Scan)
        .outerjoin(Scan.ocr_result)
        .options(contains_eager(Scan.ocr_result))
        .filter(Scan.id == scan_id)
    )
    result = db.execute(stmt).unique().scalar_one_or_none()
    if result and result.ocr_result:
        # Add statement_date to the scan object
        result.statement_date = result.ocr_result.statement_date
    return result


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
    stmt = (
        select(Scan)
        .outerjoin(Scan.ocr_result)
        .join(Scan.prospect)
        .join(Prospect.advisor)
        .options(contains_eager(Scan.ocr_result))
        .filter(Advisor.id == advisor_id)
        .offset(skip)
        .limit(limit)
    )
    results = db.execute(stmt).unique().scalars().all()

    # The statement_date will be automatically available through the property
    # we added to the Scan model
    return results


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


def create_ocr_result(
    db: Session, ocr_result_create: OcrResultSchema
) -> OcrResult:
    db_ocr_result = OcrResult(**ocr_result_create.model_dump())
    db.add(db_ocr_result)
    db.commit()
    db.refresh(db_ocr_result)
    return db_ocr_result


async def process_file(scan_id: int, advisor_id: int, document_base64):
    print(f"Processing file {scan_id} for advisor {advisor_id}")
    with SessionLocal() as db:
        print(f"Scanning document with id {scan_id}")
        statement_processor = FinancialStatementProcessor()
        results = await statement_processor.process_scan(document_base64)
        print(f"Extracted data: {scan_id}")

        new_prospect = create_prospect(
            db,
            ProspectCreateSchema(
                first_name=results["extracted_data"].investor_first_name,
                last_name=results["extracted_data"].investor_last_name,
            ),
            advisor_id,
        )

        # Create scan update with status from results
        update = ScanProcessorUpdateSchema(
            status=results["status"],
            prospect_id=new_prospect.id,
        )
        scan = update_scan(db, scan_id, update)

        # Create OCR result with all available data
        ocr_result_create = OcrResultSchema(
            scan_id=scan_id,
            statement_date=results["extracted_data"].statement_date,
            ocr_source=results["ocr_source"],
            llm_source=results["llm_source"],
            page_count=results["page_count"],
            ocr_text=results["ocr_text"],
            ocr_text_cleaned=results["ocr_text_cleaned"],
            processing_time=results["processing_time"],
        )
        ocr_result: OcrResult = create_ocr_result(db, ocr_result_create)
        for account_create in results["extracted_data"].accounts:
            create_account(db, account_create, new_prospect.id)

        db.commit()
