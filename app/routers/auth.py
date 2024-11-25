from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.schemas.auth_schema import TokenResponseSchema
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_user,
)
from app.utils.db_connection_manager import get_db
from fastapi import Cookie
from app.config import app_config

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=TokenResponseSchema)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    access_token, access_expires = create_access_token(
        user.email, str(user.id), user.role.value
    )
    refresh_token, refresh_expires = create_refresh_token(str(user.id))
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none" if app_config.DEBUG else "lax",
        expires=refresh_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": access_expires,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh_access_token(
    response: Response,
    refresh_token: str = Cookie(None),
    db: Session = Depends(get_db),
):
    user_id = verify_token(refresh_token, "refresh")
    user = get_user(db, int(user_id))
    access_token, access_expires = create_access_token(
        user.email, str(user.id), user.role.value
    )
    new_refresh_token, refresh_expires = create_refresh_token(str(user.id))
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="none" if app_config.DEBUG else "lax",
        expires=refresh_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": access_expires,
    }
