from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security.jwt import create_access_token
from app.core.security.password import (
    hash_password,
    verify_password,
)
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
)


def register_user(
    db: Session,
    user: UserCreate,
):
    existing_user = get_user_by_email(
        db,
        user.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    hashed = hash_password(user.password)

    return create_user(
        db=db,
        user=user,
        hashed_password=hashed,
    )


def login_user(
    db: Session,
    user: UserLogin,
):
    db_user = get_user_by_email(
        db,
        user.email,
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        user.password,
        db_user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(
        {
            "sub": db_user.email,
            "user_id": db_user.id,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }