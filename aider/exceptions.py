class SendCompletionError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class InvalidResponseError(Exception):
    """Raised when the LLM returns an invalid or empty response."""
    pass
