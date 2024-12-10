from fastapi import APIRouter, Depends, Response, BackgroundTasks
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
from fastapi import status, HTTPException
from app.models.schemas.auth_schema import (
    PasswordResetSchema,
    PasswordResetRequestSchema,
)
from jose import JWTError, ExpiredSignatureError
from app.models.database.user_db import User, update_user_password
from app.services.communication import EmailService


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
    user.update_login_info(db)
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


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: PasswordResetSchema, db: Session = Depends(get_db)
):
    try:
        # Verify reset token
        user_id = verify_token(request.token, "access")
        user = get_user(db, int(user_id))
        # Update password using the utility function
        update_user_password(db, user, request.new_password)

        # Notify user of successful password change
        return {"message": "Password has been successfully reset"}

    except (JWTError, ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )


@router.post(
    "/forgot-password", response_model=dict, status_code=status.HTTP_200_OK
)
async def request_password_reset(
    request: PasswordResetRequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        reset_token, _ = create_access_token(
            email=user.email,
            user_id=str(user.id),
            role=user.role.value,
            expires_delta=15 * 60,  # 15 minutes
        )

        reset_link = (
            f"{app_config.FRONTEND_URL}/reset-password?token={reset_token}"
        )

        # Create email service and send email asynchronously
        email_service = EmailService()
        background_tasks.add_task(
            email_service.send_password_reset_email,
            email=user.email,
            reset_link=reset_link,
        )

    return {"message": "If the email exists, a password reset link has been sent"}
