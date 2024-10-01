from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    status,
)
from sqlalchemy.orm import Session
from app.models.database.scan_db import (
    create_scan,
    get_scan,
    list_scans,
    delete_scan,
    update_scan,
)
from app.models.schemas.scan_schema import (
    ScanCreateSchema,
    ScanDisplaySchema,
    ScanDisplayDetailSchema,
)
from app.models.enums import ScanStatus
from app.models.database.prospect_db import get_prospect
import base64
from app.models.database.account_db import create_account
from app.models.database.holding_db import create_holding
from utils.auth import get_current_user
from utils.db_connection_manager import get_db
from app.services.statement_extractor import FinancialStatementProcessor
from app.models.database.orm_models import User


router = APIRouter(prefix="/scans", tags=["scans"])


def check_prospect_ownership(
    db: Session, advisor_id: int, prospect_id: int
) -> bool:
    """
    Check if the given user owns the specified prospect.

    :param db: Database session
    :param advisor_id: ID of the advisor
    :param prospect_id: ID of the prospect
    :return: True if the advisor owns the prospect, False otherwise
    """
    # Assuming you have a Prospect model with a relationship to the User model
    prospect = get_prospect(db, prospect_id)
    if prospect is None:
        return False

    return prospect.advisor_id == advisor_id


@router.post("/", response_model=ScanDisplaySchema)
async def upload_scan(
    file: UploadFile = File(...),
    prospect_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if the current user owns the prospect
    if not check_prospect_ownership(db, current_user.advisor.id, prospect_id):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to upload scans for this prospect",
        )

    # Read the file content
    file_content = await file.read()

    # Convert file content to base64
    base64_content = base64.b64encode(file_content).decode("utf-8")

    # Create initial scan entry
    scan_create = ScanCreateSchema(
        prospect_id=prospect_id,
        file_name=file.filename,
        uploaded_file=base64_content,
        status=ScanStatus.UPLOADED,
    )
    db_scan = create_scan(db, scan_create)

    processor_update, account_create = FinancialStatementProcessor().process_scan(
        base64_content
    )
    db_scan = update_scan(db, db_scan.id, processor_update)
    account = create_account(db, account_create, db_scan.prospect_id)
    create_holding(db, account_create.holdings, account.id)
    return scan_create


@router.get("/{scan_id}", response_model=ScanDisplayDetailSchema)
def read_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_scan = get_scan(db, scan_id)
    if db_scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Check if the current user owns the prospect associated with this scan
    if not check_prospect_ownership(
        db, current_user.advisor.id, db_scan.prospect_id
    ):
        raise HTTPException(
            status_code=403, detail="You don't have permission to access this scan"
        )

    return db_scan


@router.get("/", response_model=list[ScanDisplaySchema])
def read_scans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scans = list_scans(
        db, skip=skip, limit=limit, advisor_id=current_user.advisor.id
    )
    return scans


@router.delete("/{scan_id}", response_model=bool)
def delete_scan_route(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_code=status.HTTP_204_NO_CONTENT,
):
    db_scan = get_scan(db, scan_id)
    if db_scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Check if the current user owns the prospect associated with this scan
    if not check_prospect_ownership(
        db, current_user.advisor.id, db_scan.prospect_id
    ):
        raise HTTPException(
            status_code=403, detail="You don't have permission to delete this scan"
        )

    delete_scan(db, scan_id)
