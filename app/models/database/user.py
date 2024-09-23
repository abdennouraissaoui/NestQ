from app.models.database.schema import User
from app.models.schemas import UserBase
from sqlalchemy.orm import Session
from utils.hash import Hash
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from fastapi import HTTPException, status


user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found",
)


def create_user(db: Session, request: UserBase) -> Optional[User]:
    try:
        new_user = User(
            email=request.email,
            firm_id=request.firm_id,
            role=request.role,
            first_name=request.first_name,
            last_name=request.last_name,
            password=Hash.bcrypt(request.password),
            phone_number=request.phone_number,
        )

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

        return new_user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e.errors()}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def get_all_users(db: Session) -> List[User]:
    try:
        # TODO: Only role of admin can get all users, for their own firm only

        return db.query(User).all()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def get_user(db: Session, id: int) -> Optional[User]:
    try:
        user_data = db.query(User).filter(User.id == id).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )

    if user_data is None:
        raise user_not_found_exception
    return user_data


def update_user(db: Session, id: int, request: User) -> str:
    user = get_user(db, id)
    try:
        user.update(
            {
                user.email: request.email,
                user.role: request.role,
                user.first_name: request.first_name,
                user.last_name: request.last_name,
                user.phone_number: request.phone_number,
                user.password: Hash().bcrypt(request.password),
            }
        )
        db.commit()
        return "ok"

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def delete_user(db: Session, id: int) -> str:
    user = get_user(db, id)
    try:
        db.delete(user)
        db.commit()
        return "ok"

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
