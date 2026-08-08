class TaskNotFoundError(Exception):
    def __init__(self, message: str = "Task not found") -> None:
        super().__init__(message)
        self.message = message
