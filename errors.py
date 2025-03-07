class BaseError(Exception):
    """Base Exception"""
    pass

class S3Error(BaseError):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(f"[S3Error] {message} (Error Code: {code})")

class ScraperError(BaseError):
    def __init__(self, message):
        self.message = message
        super().__init__(f"[ScraperError] {message}")
