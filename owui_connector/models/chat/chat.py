"""
This module defines classes for managing chat references and chat sessions.
"""

from typing import Any

from .model_response import ModelChatResponse
from .user_message import UserChatMessage


class WeekChatReference:
    """
    This class represents a week reference for a chat.

    Attributes:
        id (str): The unique identifier for the chat.
        title (str): The title of the chat.
        updated_at (str): The timestamp when the chat was last updated.
        created_at (str): The timestamp when the chat was created.
    """

    id: str
    title: str
    updated_at: str
    created_at: str

    def __init__(self, chat_id: str, title: str, updated_at: str, created_at: str):
        self.id = chat_id
        self.title = title
        self.updated_at = updated_at
        self.created_at = created_at


class ChatReference:
    """
    This class represents a full chat. It contains various information's about the chat, like
    the title, used model, messages, history, tags, and timestamp to name a few.

    Attributes:
        id (str): Unique identifier for the chat.
        title (str): Title of the chat.
        models (list[str]): List of models associated with the chat.
        params (dict[str, Any]): Parameters for the chat (usage currently unknown).
        messages (list[UserChatMessage | ModelChatResponse]): List of messages in the chat.
        history (dict[str, Any]): History of the chat messages.
        tags (list[str]): List of tags associated with the chat.
        timestamp (int): Timestamp of the chat creation.
    """

    id: str
    title: str
    models: list[str]
    params: dict[str, Any]
    messages: list[UserChatMessage | ModelChatResponse]
    history: dict[str, Any]
    tags: list[str]
    timestamp: int

    def __init__(
        self,
        chat_id: str,
        title: str,
        models: list[str],
        params: dict[str, Any],  # TODO: I dont know what this is for at the moment
        messages: list[UserChatMessage | ModelChatResponse],
        history: dict[str, Any] | None,
        tags: list[str],
        timestamp: int,
    ):
        self.id = chat_id
        self.title = title
        self.models = models
        self.messages = messages
        self.params = params

        if not history:
            history_result = self.chat_messages_to_history(messages)
            self.history = history_result
        else:
            # TODO: check if there is already a history, and append it
            self.history = history

        self.tags = tags
        self.timestamp = timestamp

    def chat_messages_to_history(
        self, messages: list[UserChatMessage | ModelChatResponse]
    ) -> dict[str, Any]:
        """
        Converts a list of chat messages to a history dictionary.

        Args:
            messages (list[UserChatMessage | ModelChatResponse]): A list of chat messages,
                which can be either UserChatMessage or ModelChatResponse instances.

        Returns:
        -------
            dict[str, Any]: A dictionary containing the chat history with the following keys:
                - "messages": A dictionary where the keys are message IDs and the values are
                  the message data converted to a dictionary.
                - "currentId": The ID of the most recent message, or None if the messages
                  list is empty.
        """
        history = {
            "messages": {message.id: message.to_dict(True) for message in messages},
            "currentId": messages[-1].id if messages else None,
        }

        return history

    def to_dict(self, is_new: bool = False):
        """
        Converts the chat object to a dictionary representation.

        Args:
            is_new (bool): A flag indicating whether the chat is new. Defaults to False.

        Returns:
            dict: A dictionary representation of the chat object with keys formatted
                  correctly and messages converted to dictionaries.
        """
        chat_dict = self.__dict__.copy()
        # convert the var names to the correct format
        messages_list = [
            message.to_dict(is_new)
            for message in self.messages
            if hasattr(message, "to_dict")
        ]

        for key, value in chat_dict.items():
            if "_" in key:
                # delete the underscore and capitalize only the first character after it
                new_key = key.split("_", 1)[0] + "".join(
                    word.capitalize() if i == 0 else word
                    for i, word in enumerate(key.split("_")[1:])
                )
                chat_dict[new_key] = value
                del chat_dict[key]

        chat_dict["messages"] = messages_list
        return chat_dict


class Chat:
    """
    Top level class for a chat object.
    """

    chat: ChatReference

    def __init__(
        self,
        chat: ChatReference,
    ):
        self.chat = chat

    def to_dict(self, is_new: bool = False):
        """
        Converts the chat object to a dictionary, with optional formatting for new objects.

        Args:
            is_new (bool): If True, indicates that the object is new and may require special handling.

        Returns:
            dict: A dictionary representation of the chat object with keys formatted correctly.
        """
        chat_dict = self.__dict__.copy()
        # convert the var names to the correct format
        for key, value in chat_dict.items():
            if "_" in key:
                # delete the underscore and capitalize the next character
                new_key = key.split("_", 1)[0] + "".join(
                    word.capitalize() for word in key.split("_")[1:]
                )
                chat_dict[new_key] = value
                del chat_dict[key]

        # convert the child objects to a dictionary
        chat_dict["chat"] = self.chat.to_dict(is_new)
        return chat_dict
