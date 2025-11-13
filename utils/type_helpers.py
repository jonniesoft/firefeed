"""Type safety helper functions for common patterns.

This module provides utilities to safely handle potentially None values,
type conversions, and dynamic types from external libraries.
"""

from typing import Any, TypeVar

T = TypeVar("T")


def safe_get_attr(obj: Any, attr: str, default: T) -> T:
    """Safely get attribute from potentially None object.

    Args:
        obj: Object to get attribute from (can be None)
        attr: Attribute name
        default: Default value if obj is None or attribute doesn't exist

    Returns:
        Attribute value or default

    Example:
        >>> user = None
        >>> name = safe_get_attr(user, 'name', 'Anonymous')
        >>> # returns 'Anonymous'
    """
    return getattr(obj, attr, default) if obj is not None else default


def safe_feed_text(value: Any) -> str:
    """Extract text from FeedParserDict value (str, list, or None).

    FeedParser can return values in different formats:
    - str: direct text value
    - list[FeedParserDict]: multiple values, take first
    - None: missing value

    Args:
        value: Value from FeedParserDict (title, link, etc.)

    Returns:
        Extracted and cleaned text string

    Example:
        >>> title = safe_feed_text(entry.get('title'))
        >>> # Handles str, list, or None safely
    """
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list) and value:
        first = value[0]
        return str(first).strip() if first else ""
    return ""


def ensure_not_none(value: T | None, name: str) -> T:
    """Assert value is not None, raise ValueError if it is.

    Args:
        value: Value to check
        name: Variable name for error message

    Returns:
        Value if not None

    Raises:
        ValueError: If value is None

    Example:
        >>> user_id = ensure_not_none(update.message.from_user.id, "user_id")
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    return value


def bytes_to_str(value: bytes | str) -> str:
    """Convert bytes to str, or return str as-is.

    Useful for handling database results where some fields
    might be returned as bytes instead of str.

    Args:
        value: Bytes or string value

    Returns:
        String (decoded if was bytes)

    Example:
        >>> text = bytes_to_str(row[b'title'])  # handles bytes keys
        >>> # returns decoded string
    """
    return value.decode("utf-8") if isinstance(value, bytes) else value
