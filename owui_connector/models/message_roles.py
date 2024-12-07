"""
This file holds a class for the message roles in the chat model.
"""

from enum import Enum


class MessageRoles(Enum):
    """
    Enum class representing different roles in a messaging system.

    Attributes:
        USER (str): Represents a user role.
        ASSISTENT (str): Represents an assistant role.
    """

    USER = "user"
    ASSISTENT = "assistent"
