from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from utils.auth import get_current_user

from app.models.database import account_db
from app.models.database.schema import User, Holding
from app.models.schemas import AccountListDisplay, AccountDetailDisplay, AccountUpdate
from utils.db_connection_manager import get_db


router = APIRouter(
    prefix="/account",
    tags=["Account"],
)


@router.get(
    "/prospect/{prospect_id}",
    response_model=List[AccountListDisplay],
    status_code=status.HTTP_200_OK,
)
def get_accounts_by_prospect(
    prospect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a list of accounts for a given prospect.
    """
    # Authorization checks
    if not account_db.is_advisor_prospect(db, current_user.advisor.id, prospect_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these accounts",
        )

    accounts = account_db.get_accounts_by_prospect(db, prospect_id)
    return accounts


@router.get(
    "/{account_id}",
    response_model=AccountDetailDisplay,
    status_code=status.HTTP_200_OK,
)
def get_account_by_id(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get account details by account ID, including holdings.
    """
    # Authorization checks

    if not account_db.is_advisor_account(db, current_user.advisor.id, account_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )

    account = account_db.get_account_by_id(db, account_id)
    return account


@router.put(
    "/{account_id}",
    response_model=AccountDetailDisplay,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing account's information.
    """
    # Authorization checks
    if not account_db.is_advisor_account(db, current_user.advisor.id, account_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this account",
        )

    updated_account = account_db.update_account(db, account_id, account_update)
    # Fetch the holdings after update
    updated_account.holdings = (
        db.query(Holding).filter(Holding.account_id == account_id).all()
    )
    return updated_account
