from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models.conversation import Conversation, Message


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        owner_id: str,
        title: str | None = None,
        project_id: str | None = None,
    ) -> Conversation:
        conversation = Conversation(
            owner_id=owner_id,
            project_id=project_id,
            title=title,
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: str) -> Conversation | None:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def list_by_owner(self, owner_id: str) -> list[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.owner_id == owner_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    def add_message(
        self,
        *,
        conversation_id: str,
        role: str,
        content: str,
        status: str = "completed",
        asset_id: str | None = None,
        error_message: str | None = None,
        extra_metadata: dict | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            status=status,
            asset_id=asset_id,
            error_message=error_message,
            extra_metadata=extra_metadata,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message