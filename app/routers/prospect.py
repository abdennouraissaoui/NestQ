from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.schemas import (
    Prospect as ProspectSchema,
    ProspectDisplay,
    ProspectDetailDisplay,
    ProspectPut,
)
from app.models.database.prospect_db import (
    create_prospect,
    get_prospects_by_advisor,
    get_prospect,
    update_prospect,
    delete_prospect,
)
from app.models.database.document_db import get_documents_by_prospect_id
from utils.auth import get_current_user, get_db
from app.models.database.user_db import User
from app.models.enums import Role

router = APIRouter(prefix="/prospects", tags=["Prospects"])


def get_prospect_or_404(prospect_id: int, db: Session, current_user: User):
    prospect = get_prospect(db, prospect_id)
    if (
        not prospect
        or not current_user.advisor
        or prospect.advisor_id != current_user.advisor.id
    ):
        raise HTTPException(status_code=404, detail="Prospect not found")
    return prospect


@router.post(
    "/",
    response_model=ProspectDisplay,
    summary="Create a new prospect",
    description="Create a new prospect associated with the current advisor.",
    response_description="The created prospect.",
)
def create_prospect_route(
    prospect: ProspectPut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != Role.ADVISOR:
        raise HTTPException(
            status_code=403, detail="Only advisors can create prospects"
        )
    if not current_user.advisor:
        raise HTTPException(
            status_code=400, detail="Current user is not associated with an advisor"
        )
    prospect_data = ProspectSchema(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        advisor_id=current_user.advisor.id,
    )
    return create_prospect(db, prospect_data)


@router.get(
    "/",
    response_model=List[ProspectDisplay],
    summary="Get a list of prospects",
    description="Retrieve a list of prospects associated with the current advisor.",
    response_description="A list of prospects.",
)
def get_prospects_route(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role != Role.ADVISOR:
        raise HTTPException(status_code=403, detail="Only advisors can view prospects")
    return get_prospects_by_advisor(db, current_user.advisor.id)


@router.get(
    "/{prospect_id}",
    response_model=ProspectDetailDisplay,
    summary="Get a prospect by ID",
    description="Retrieve a prospect by ID along with their associated documents.",
    response_description="The retrieved prospect with documents.",
)
def get_prospect_route(
    prospect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prospect = get_prospect_or_404(prospect_id, db, current_user)
    documents = get_documents_by_prospect_id(db, prospect_id)
    return ProspectDetailDisplay(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        documents=[doc.filename for doc in documents],
    )


@router.put(
    "/{prospect_id}",
    response_model=ProspectDetailDisplay,
    summary="Update a prospect by ID",
    description="Update the details of a prospect by their ID.",
    response_description="The updated prospect.",
)
def update_prospect_route(
    prospect_id: int,
    prospect_update: ProspectPut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prospect = get_prospect_or_404(prospect_id, db, current_user)
    return update_prospect(db, prospect, prospect_update)


@router.delete(
    "/{prospect_id}",
    response_model=ProspectDisplay,
    summary="Delete a prospect by ID",
    description="Delete a prospect by their ID.",
    response_description="The deleted prospect.",
)
def delete_prospect_route(
    prospect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_prospect_or_404(prospect_id, db, current_user)
    return delete_prospect(db, prospect_id)
