from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.database.orm_models import Account, Holding, Scan
from app.models.schemas.account_schema import (
    AccountUpdateSchema,
    AccountCreateSchema,
)

account_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Account not found",
)

scan_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Scan not found",
)


def _get_account_or_raise(db: Session, account_id: int) -> Account:
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise account_not_found_exception
    return account


def is_advisor_scan(db: Session, advisor_id: int, scan_id: int) -> bool:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise scan_not_found_exception
    return scan.prospect.advisor.id == advisor_id


def is_advisor_account(db: Session, advisor_id: int, account_id: int) -> bool:
    account = _get_account_or_raise(db, account_id)
    return account.scan.prospect.advisor.id == advisor_id


def get_accounts_by_scan(db: Session, scan_id: int) -> List[Account]:
    accounts = db.query(Account).filter(Account.scan_id == scan_id).all()
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No accounts found for scan with id {scan_id}",
        )
    return accounts


def get_account_by_id(db: Session, account_id: int) -> Account:
    account = _get_account_or_raise(db, account_id)
    # Explicitly load the holdings
    account.holdings = (
        db.query(Holding).filter(Holding.account_id == account_id).all()
    )
    return account


def update_account(
    db: Session, account_id: int, account_update: AccountUpdateSchema
) -> Account:
    account = _get_account_or_raise(db, account_id)
    for field, value in account_update.dict(exclude_unset=True).items():
        setattr(account, field, value)
    db.commit()
    db.refresh(account)
    return account


def create_account(
    db: Session, account_create: AccountCreateSchema, scan_id: int
) -> Account:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise scan_not_found_exception

    # Create the account
    account_data = account_create.model_dump(exclude={"id", "holdings"})
    db_account = Account(**account_data, scan_id=scan_id)
    db.add(db_account)
    db.flush()  # This assigns an ID to db_account without committing the transaction

    # Create holdings
    for holding_data in account_create.holdings:
        db_holding = Holding(
            **holding_data.model_dump(exclude={"id"}), account_id=db_account.id
        )
        db.add(db_holding)
    db.commit()
    db.refresh(db_account)

    return db_account
