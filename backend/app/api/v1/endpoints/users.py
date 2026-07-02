from fastapi import APIRouter, Depends

from app.database.models import User
from app.dependencies.auth import get_current_user
from app.schemas.user import UserProfileResponse

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