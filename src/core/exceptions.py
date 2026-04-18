class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# --- Subscriber exceptions ---

class SubscriberAlreadyExistsError(AppException):
    def __init__(self, email: str):
        super().__init__(f"Subscriber already exists: {email}")


class SubscriberNotFoundError(AppException):
    def __init__(self, email: str):
        super().__init__(f"Subscriber not found: {email}")


class InvalidCSVError(AppException):
    def __init__(self, reason: str):
        super().__init__(f"Invalid CSV file: {reason}")


# --- Newsletter / rendering exceptions ---

class MarkdownFileError(AppException):
    def __init__(self, path: str, reason: str):
        super().__init__(f"Cannot read markdown file '{path}': {reason}")


class ImageNotFoundError(AppException):
    def __init__(self, path: str):
        super().__init__(f"Image file not found: {path}")


class ImageUploadError(AppException):
    def __init__(self, path: str, reason: str):
        super().__init__(f"Failed to upload '{path}': {reason}")


# --- Email exceptions ---

class EmailSendError(AppException):
    def __init__(self, email: str, reason: str):
        super().__init__(f"Failed to send to {email}: {reason}")
