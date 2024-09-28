from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Optional
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from app.models.database.user_db import User, get_user
from utils.hash import Hash
from fastapi import HTTPException, status, Depends
from app.config import app_config
from utils.db_connection_manager import get_db
from sqlalchemy.orm import Session


SECRET_KEY = app_config.AUTH_SECRET_KEY
ALGORITHM = app_config.AUTH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = app_config.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def authenticate_user(email: str, password: str, db) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception
    if not Hash.verify(hashed_password=user.password, plain_password=password):
        raise credentials_exception
    # Update last_login and increment sign_in_count
    current_time = int(datetime.now(timezone.utc).timestamp())
    user.last_login = current_time
    user.sign_in_count += 1
    db.commit()
    return user


def create_access_token(
    email: str,
    user_id: str,
    role: str,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
):
    encode = {"sub": email, "id": user_id, "role": role}

    expires = datetime.now(timezone.utc) + expires_delta

    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise credentials_exception
        return get_user(db, user_id)

    except JWTError:
        raise credentials_exception
