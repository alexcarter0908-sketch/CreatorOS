import uuid


class CommandService:
    def execute(self, project_id: str, command: str):
        return {
            "executionId": str(uuid.uuid4()),
            "status": "completed",
            "projectId": project_id,
            "command": command,
        }