from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError, ExpiredSignatureError
from app.models.database.user_db import User, get_user
from utils.hash import Hash
from fastapi import HTTPException, status, Depends
from app.config import app_config
from utils.db_connection_manager import get_db
from sqlalchemy.orm import Session
from time import time


SECRET_KEY = app_config.AUTH_SECRET_KEY
ALGORITHM = app_config.AUTH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = app_config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 1  # You can move this to app_config if needed

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)


def authenticate_user(email: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not Hash.verify(hashed_password=user.password, plain_password=password):
        raise credentials_exception
    return user


def create_access_token(
    email: str,
    user_id: str,
    role: str,
    expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60,
):
    encode = {"sub": email, "id": user_id, "role": role, "type": "access"}
    expires = int(time()) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM), expires


def create_refresh_token(user_id: str):
    encode = {"id": user_id, "type": "refresh"}
    expires = int(time()) + (REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM), expires


def verify_token(token: str, token_type: str):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        token_type_from_payload: str = payload.get("type")
        if user_id is None or token_type_from_payload != token_type:
            raise credentials_exception
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    user_id = verify_token(token, "access")
    user = get_user(db, int(user_id))
    if user is None:
        raise credentials_exception
    return user
