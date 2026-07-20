from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation import (
    ConversationDetailResponse,
    ConversationResponse,
    CreateConversationRequest,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ConversationRepository(db)
    return repo.create(
        owner_id=current_user.id,
        title=request.title,
        project_id=request.project_id,
    )


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ConversationRepository(db)
    return repo.list_by_owner(current_user.id)


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ConversationRepository(db)
    conversation = repo.get_by_id(conversation_id)

    if conversation is None or conversation.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return conversation
