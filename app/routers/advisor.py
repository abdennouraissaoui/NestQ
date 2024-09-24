from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from utils.auth import get_current_user

from app.models.database import advisor_db
from app.models.database.schema import User
from app.models.schemas import AdvisorDisplay, AdvisorDetailDisplay, ProspectDisplay
from utils.db_connection_manager import get_db
from app.models.enums import Role  # Ensure Role is imported


router = APIRouter(prefix="/advisor", tags=["Advisor"])


@router.get("/", response_model=List[AdvisorDisplay], status_code=status.HTTP_200_OK)
def get_advisors(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get a list of advisors belonging to the current user's firm.
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access advisors list",
        )
    firm_id = current_user.firm_id
    advisors = advisor_db.get_advisors_by_firm(db, firm_id)
    advisors_display = [
        AdvisorDisplay(
            id=advisor.id,
            first_name=advisor.user.first_name,
            last_name=advisor.user.last_name,
            created_at=advisor.created_at,
        )
        for advisor in advisors
    ]
    return advisors_display


@router.get(
    "/{advisor_id}", response_model=AdvisorDetailDisplay, status_code=status.HTTP_200_OK
)
def get_advisor(
    advisor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a single advisor by ID, including their list of prospects.
    """
    advisor = advisor_db.get_advisor(db, advisor_id)

    if current_user.role == Role.ADMIN:
        if advisor.user.firm_id != current_user.firm_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this advisor",
            )
    elif current_user.id != advisor.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this advisor",
        )
    # Build the response
    prospects_display = [
        ProspectDisplay(
            id=prospect.id,
            first_name=prospect.first_name,
            last_name=prospect.last_name,
            created_at=prospect.created_at,
            updated_at=prospect.updated_at,
        )
        for prospect in advisor.user.prospects
    ]
    return AdvisorDetailDisplay(
        id=advisor.id,
        first_name=advisor.user.first_name,
        last_name=advisor.user.last_name,
        created_at=advisor.created_at,
        prospects=prospects_display,
    )


# @router.put(
#     "/{advisor_id}", response_model=AdvisorDisplay, status_code=status.HTTP_202_ACCEPTED
# )
# def update_advisor(
#     advisor_id: int,
#     updated_data: dict,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Update an existing advisor's information.
#     """
#     advisor = advisor_db.get_advisor(db, advisor_id)
#     # Authorization checks
#     if current_user.role == Role.ADMIN:
#         if advisor.user.firm_id != current_user.firm_id:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Not authorized to update this advisor",
#             )
#     elif current_user.id != advisor.user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update this advisor",
#         )
#     updated_advisor = advisor_db.update_advisor(db, advisor_id, updated_data)
#     return AdvisorDisplay(
#         id=updated_advisor.id,
#         first_name=updated_advisor.user.first_name,
#         last_name=updated_advisor.user.last_name,
#         created_at=updated_advisor.created_at,
#     )
