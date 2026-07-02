from pydantic import BaseModel


class CommandRequest(BaseModel):
    projectId: str
    command: str


class CommandResponse(BaseModel):
    executionId: str
    status: str