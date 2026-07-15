"""Application-specific exceptions."""


class ShoppingCartError(ValueError):
    """Base class for errors that can be shown safely to the user."""


class InputFormatError(ShoppingCartError):
    """Raised when the text input does not follow the expected format."""


class ValidationError(ShoppingCartError):
    """Raised when parsed data violates a business constraint."""
