from sqlalchemy.orm import Session
from app.models.database.schema import Advisor, User, Prospect
from fastapi import HTTPException, status
from typing import List

advisor_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Advisor not found",
)


# Add the following helper function to avoid duplicate code
def _get_advisor_or_raise(db: Session, advisor_id: int) -> Advisor:
    advisor = db.query(Advisor).filter(Advisor.id == advisor_id).first()
    if not advisor:
        raise advisor_not_found_exception
    return advisor


def get_advisor(db: Session, advisor_id: int) -> Advisor:
    """
    Retrieve an advisor by ID.
    """
    # Use the helper function
    return _get_advisor_or_raise(db, advisor_id)


def get_advisors_by_firm(db: Session, firm_id: int) -> List[Advisor]:
    """
    Retrieve all advisors belonging to a specific firm.
    """
    advisors = db.query(Advisor).join(User).filter(User.firm_id == firm_id).all()
    return advisors


def create_advisor(db: Session, user_id: int) -> Advisor:
    """
    Create a new advisor linked to a user.
    """
    new_advisor = Advisor(user_id=user_id)
    db.add(new_advisor)
    db.commit()
    db.refresh(new_advisor)
    return new_advisor


def update_advisor(db: Session, advisor_id: int, updated_data: dict) -> Advisor:
    """
    Update an advisor's information.
    """
    # Use the helper function
    advisor = _get_advisor_or_raise(db, advisor_id)
    for key, value in updated_data.items():
        setattr(advisor, key, value)
    db.commit()
    db.refresh(advisor)
    return advisor


def delete_advisor(db: Session, advisor_id: int):
    """
    Delete an advisor.
    """
    # Use the helper function
    advisor = _get_advisor_or_raise(db, advisor_id)
    db.delete(advisor)
    db.commit()
