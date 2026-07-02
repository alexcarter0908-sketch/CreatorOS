from app.database.base import Base
from app.database.session.database import engine

# Import all models
from app.database.models import User, Project


def init_database() -> None:
    Base.metadata.create_all(bind=engine)