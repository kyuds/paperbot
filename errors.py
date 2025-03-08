# custom error types for paperbot

class BaseError(Exception):
    """Base Exception"""
    pass

class S3Error(BaseError):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code
        super().__init__(f"[S3Error] {message} (Error Code: {code})")

class ScraperError(BaseError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"[ScraperError] {message}")
