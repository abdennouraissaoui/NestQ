from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.models.schemas import Token
from utils.db_connection_manager import get_db
from utils.auth import create_access_token, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(user.email, str(user.id), user.role.value)
    return {"access_token": token, "token_type": "bearer"}
