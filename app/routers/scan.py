from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    # Form,
    status,
)
from sqlalchemy.orm import Session
from app.models.database.scan_db import (
    create_scan,
    get_scan,
    list_scans,
    delete_scan,
)
from app.models.schemas.scan_schema import (
    ScanCreateSchema,
    ScanDisplaySchema,
    ScanDisplayDetailSchema,
)
from app.models.enums import ScanStatus
from app.models.database.prospect_db import get_prospect
import base64
from app.utils.auth import get_current_user
from app.utils.db_connection_manager import get_db
from app.models.database.orm_models import User
from fastapi.responses import StreamingResponse
from app.models.database.scan_db import process_scan
from fastapi import BackgroundTasks
from asyncio import sleep


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


async def get_scan_status_stream(
    scan_id: int,
    db: Session,
    timeout: int = 300,
    initial_wait: int = 15,
    interval: int = 3,
):
    """
    Get the status of a scan. Times out after timeout seconds.
    """
    await sleep(initial_wait)
    elapsed = initial_wait
    scan = get_scan(db, scan_id)
    while True:
        db.refresh(scan)
        if scan.status in [ScanStatus.PROCESSED, ScanStatus.ERROR]:
            yield f"data: {scan.status.value}\n\n"
            break
        await sleep(interval)
        elapsed += interval
        if elapsed > timeout:
            yield f"data: {ScanStatus.ERROR.value}\n\n"
            break


@router.get("/{scan_id}/status")
async def get_scan_status(
    scan_id: int,
    db: Session = Depends(get_db),
):
    """
    Get the status of a scan.
    """
    scan = get_scan(db, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    return StreamingResponse(
        get_scan_status_stream(scan_id, db), media_type="text/event-stream"
    )


@router.post("/", response_model=ScanDisplaySchema)
async def upload_scan(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    # Read the file content
    file_content = await file.read()

    # Convert file content to base64
    base64_content = base64.b64encode(file_content).decode("utf-8")

    # Create initial scan entry
    scan_create = ScanCreateSchema(
        file_name=file.filename,
        uploaded_file=base64_content,
        status=ScanStatus.PROCESSING,
    )

    db_scan = create_scan(db, scan_create)

    background_tasks.add_task(
        process_scan, db_scan.id, current_user.advisor.id, base64_content
    )
    return db_scan


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


@router.delete("/{scan_id}")
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
