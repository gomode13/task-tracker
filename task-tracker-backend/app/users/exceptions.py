class EmailAlreadyTakenError(Exception):
    def __init__(self, message: str = "This email is already taken") -> None:
        super().__init__(message)
        self.message = message
