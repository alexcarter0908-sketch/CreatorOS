from app.database.base import Base
from app.database.session.database import engine

from app.database.models import (
    User,
    Project,
    Asset,
    AutoTarget,
    Workflow,
    WorkflowStep,
    PublishAccount,
)


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
