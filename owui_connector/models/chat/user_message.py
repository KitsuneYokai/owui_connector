"""
This module defines a class for using chat messages in the chat model.
"""


class UserChatMessage:
    """
    UserChatMessage represents a chat message with attributes for message ID,
    parent ID, children IDs, role, content, timestamp, and models.

    Attributes:
        id (str): Unique identifier for the message.
        parent_id (str | None): Identifier of the parent message, if any.
        children_ids (list[str]): List of identifiers for child messages.
        role (str): Role of the message sender.
        content (str): Content of the message.
        timestamp (int): Timestamp of when the message was created.
        models (list[str]): List of models associated with the message.
    """

    id: str
    parent_id: str | None
    children_ids: list[str]
    role: str
    content: str
    timestamp: int
    models: list[str]

    def __init__(
        self,
        message_id: str,
        parent_id: str | None,
        children_ids: list[str],
        role: str,
        content: str,
        timestamp: int,
        models: list[str],
    ):
        self.id = message_id
        self.parent_id = parent_id
        self.children_ids = children_ids
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.models = models

    def to_dict(self, _):
        """
        Converts the instance's attributes to a dictionary, modifying the keys to a specific format.

        The method creates a copy of the instance's `__dict__` attribute and then processes each key
        to remove underscores and capitalize the first character of each subsequent word.

        Args:
            _: Unused parameter.

        Returns:
            dict: A dictionary representation of the instance with formatted keys.
        """
        chat_dict = self.__dict__.copy()
        # convert the var names to the correct format
        for key in list(chat_dict.keys()):
            if "_" in key:
                # delete the underscore and capitalize only the first character after it
                new_key = key.split("_", 1)[0] + "".join(
                    word.capitalize() for word in key.split("_")[1:]
                )
                chat_dict[new_key] = chat_dict.pop(key)

        return chat_dict
