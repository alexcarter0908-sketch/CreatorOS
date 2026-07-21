from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserProfileResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserProfileResponse,
)
def update_me(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url
    if request.notify_email_digest is not None:
        current_user.notify_email_digest = request.notify_email_digest
    if request.notify_low_credit_email is not None:
        current_user.notify_low_credit_email = request.notify_low_credit_email

    UserRepository(db).update(current_user)
    return current_user


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google Sign-In and has no password to change.",
        )

    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect.",
        )

    current_user.password_hash = hash_password(request.new_password)
    UserRepository(db).update(current_user)
    return None


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_me(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Permanently deletes the current user and everything owned by them
    (projects, assets, workflows, notifications, billing history, ...)
    via the ON DELETE CASCADE foreign keys already on those tables.
    Cannot be undone.
    """
    if current_user.password_hash:
        if not request.password or not verify_password(request.password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is incorrect.",
            )

    UserRepository(db).delete(current_user)
    return None
