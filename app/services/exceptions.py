"""Custom exceptions for service layer.

This module defines domain-specific exceptions that map to appropriate HTTP status codes:
- InvalidInputError → 400 Bad Request
- OmniParserError → 422 Unprocessable Entity
- ModelInferenceError → 503 Service Unavailable
- RAGKnowledgeBaseError → 503 Service Unavailable
"""


class ServiceException(Exception):
    """Base exception for all service-layer errors."""

    def __init__(self, message: str, details: dict = None):
        """Initialize service exception.

        Args:
            message: Human-readable error message
            details: Additional error context (optional)
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidInputError(ServiceException):
    """Raised when input validation fails.

    Maps to HTTP 400 Bad Request.
    """

    pass


class OmniParserError(ServiceException):
    """Raised when OmniParser detection or processing fails.

    Maps to HTTP 422 Unprocessable Entity.
    """

    pass


class ModelInferenceError(ServiceException):
    """Raised when LLM inference fails.

    Maps to HTTP 503 Service Unavailable.
    """

    pass


class RAGKnowledgeBaseError(ServiceException):
    """Raised when knowledge base operations fail.

    Maps to HTTP 503 Service Unavailable.
    """

    pass
