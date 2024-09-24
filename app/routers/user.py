from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from utils.db_connection_manager import get_db
from app.models.database import user_db
from app.models.schemas import UserBase, UserDisplay
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from app.models.enums import Role  # Import the Role enum

router = APIRouter(prefix="/user", tags=["user"])

# Define the exception
forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource"
)


def check_admin_and_firm(current_user: UserBase, user_firm_id: int):
    if current_user.role != Role.ADMIN or current_user.firm_id != user_firm_id:
        raise forbidden_exception


@router.post("/", response_model=UserDisplay)
def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
    status_code=status.HTTP_201_CREATED,
):
    return user_db.create_user(db, request)


@router.get("/", response_model=List[UserDisplay])
def get_all_users(
    db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)
):
    if current_user.role != Role.ADMIN:
        raise forbidden_exception
    users_list = user_db.get_all_users_by_firm(
        db, current_user.firm_id
    )  # Filter by firm
    return users_list


@router.get("/{id}", response_model=UserDisplay)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    user = user_db.get_user(db, id)
    check_admin_and_firm(current_user, user.firm_id)
    return user


@router.put("/{id}", response_model=UserDisplay)
def update_user(
    id: int,
    request: UserBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    user = user_db.get_user(db, id)
    check_admin_and_firm(current_user, user.firm_id)
    return user_db.update_user(db, id, request)


@router.delete("/{id}", response_model=UserDisplay)
def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    user = user_db.get_user(db, id)
    check_admin_and_firm(current_user, user.firm_id)
    return user_db.delete_user(db, id)
