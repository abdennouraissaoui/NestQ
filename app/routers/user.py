from typing import List
from fastapi import APIRouter, Depends, status
from utils.db_connection_manager import get_db
from app.models.database import user
from app.models.schemas import UserBase, UserDisplay
from sqlalchemy.orm import Session
from utils.auth import get_current_user


router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", response_model=UserDisplay)
def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
    status_code=status.HTTP_201_CREATED,
):
    return user.create_user(db, request)


@router.get("/", response_model=List[UserDisplay])
def get_all_users(
    db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)
):
    users_list = user.get_all_users(db)
    return users_list


# Read one user


@router.get("/{id}", response_model=UserDisplay)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return user.get_user(db, id)


# Update user


@router.post("/{id}/update")
def update_user(
    id: int,
    request: UserBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return user.update_user(db, id, request)


# Delete user


@router.get("/delete/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return user.delete_user(db, id)
