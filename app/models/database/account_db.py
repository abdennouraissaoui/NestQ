from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.database.schema import Account, Prospect, Holding
from app.models.schemas import AccountUpdate

account_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Account not found",
)

prospect_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Prospect not found",
)


def _get_account_or_raise(db: Session, account_id: int) -> Account:
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise account_not_found_exception
    return account


def is_advisor_prospect(db: Session, advisor_id: int, prospect_id: int) -> bool:
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not prospect:
        raise prospect_not_found_exception
    return prospect.advisor.id == advisor_id


def is_advisor_account(db: Session, advisor_id: int, account_id: int) -> bool:
    account = _get_account_or_raise(db, account_id)
    return account.prospect.advisor.id == advisor_id


def get_accounts_by_prospect(db: Session, prospect_id: int) -> List[Account]:
    accounts = db.query(Account).filter(Account.prospect_id == prospect_id).all()
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No accounts found for prospect with id {prospect_id}",
        )
    return accounts


def get_account_by_id(db: Session, account_id: int) -> Account:
    account = _get_account_or_raise(db, account_id)
    # Explicitly load the holdings
    account.holdings = db.query(Holding).filter(Holding.account.id == account_id).all()
    return account


def update_account(
    db: Session, account_id: int, account_update: AccountUpdate
) -> Account:
    account = _get_account_or_raise(db, account_id)
    for field, value in account_update.dict(exclude_unset=True).items():
        setattr(account, field, value)
    db.commit()
    db.refresh(account)
    return account
