from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.schemas import (
    Prospect as ProspectSchema,
    ProspectDisplay,
    ProspectDetailDisplay,
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

router = APIRouter()


@router.post("/", response_model=ProspectDisplay)
def create_prospect_route(
    prospect: ProspectSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != Role.advisor:
        raise HTTPException(
            status_code=403, detail="Only advisors can create prospects"
        )
    return create_prospect(db, prospect)


@router.get("/", response_model=List[ProspectDisplay])
def get_prospects_route(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role != Role.advisor:
        raise HTTPException(status_code=403, detail="Only advisors can view prospects")
    return get_prospects_by_advisor(db, current_user.id)


@router.get("/{prospect_id}", response_model=ProspectDetailDisplay)
def get_prospect_route(
    prospect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prospect = get_prospect(db, prospect_id)
    if not prospect or prospect.advisor_id != current_user.id:
        raise HTTPException(status_code=404, detail="Prospect not found")
    documents = get_documents_by_prospect_id(db, prospect_id)
    return ProspectDetailDisplay(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        documents=[doc.filename for doc in documents],
    )


@router.put("/{prospect_id}", response_model=ProspectDetailDisplay)
def update_prospect_route(
    prospect_id: int,
    first_name: str,
    last_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prospect = get_prospect(db, prospect_id)
    if not prospect or prospect.advisor_id != current_user.id:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return update_prospect(db, prospect_id, first_name, last_name)


@router.delete("/{prospect_id}", response_model=ProspectDisplay)
def delete_prospect_route(
    prospect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prospect = get_prospect(db, prospect_id)
    if not prospect or prospect.advisor_id != current_user.id:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return delete_prospect(db, prospect_id)
