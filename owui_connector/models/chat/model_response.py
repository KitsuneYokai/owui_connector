"""
This module defines the ModelChatResponseInfo and ModelChatResponse classes, which represent
the response information and the response itself in a chat model, respectively.
"""


class ModelChatResponseInfo:
    """
    ModelChatResponseInfo class represents the response information for a chat model.
    Attributes:
        total_duration (int): The total duration of the chat response.
        load_duration (int): The duration taken to load the chat model.
        prompt_eval_count (int): The count of prompt evaluations.
        prompt_eval_duration (int): The duration of prompt evaluations.
        eval_count (int): The count of evaluations.
        eval_duration (int): The duration of evaluations.

    Methods:
        __init__(self, total_duration: int, load_duration: int, prompt_eval_count: int,
                 prompt_eval_duration: int, eval_count: int, eval_duration: int):
            Initializes the ModelChatResponseInfo with the provided durations and counts.
        to_dict(self):
            Converts the instance and its attributes to a dictionary,
            modifying attribute names by removing underscores and capitalizing the
            following character.
    """

    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int

    def __init__(
        self,
        total_duration: int,
        load_duration: int,
        prompt_eval_count: int,
        prompt_eval_duration: int,
        eval_count: int,
        eval_duration: int,
    ):
        self.total_duration = total_duration
        self.load_duration = load_duration
        self.prompt_eval_count = prompt_eval_count
        self.prompt_eval_duration = prompt_eval_duration
        self.eval_count = eval_count
        self.eval_duration = eval_duration

    def to_dict(self):
        """
        Converts the instance attributes to a dictionary with formatted keys.

        This method creates a copy of the instance's `__dict__` and modifies the keys
        by removing underscores and capitalizing the first character of each subsequent word.

        Returns:
            dict: A dictionary representation of the instance with formatted keys.
        """

        chat_dict = self.__dict__.copy()
        # convert the var names to the correct format
        for key, value in chat_dict.items():
            if "_" in key:
                # delete the underscore and capitalize only the first character after it
                new_key = key.split("_", 1)[0] + "".join(
                    word.capitalize() if i == 0 else word
                    for i, word in enumerate(key.split("_")[1:])
                )
                chat_dict[new_key] = value
                del chat_dict[key]

        return chat_dict


class ModelChatResponse:
    """
    ModelChatResponse represents a response in a chat model.

    Attributes:
        parent_id (str): The ID of the parent message.
        id (str): The ID of the current message.
        children_ids (list[str]): A list of IDs of the child messages.
        role (str): The role of the message sender.
        content (str): The content of the message.
        model (str): The model used for generating the response.
        model_name (str): The name of the model.
        user_context (str | None): The context of the user.
        timestamp (int): The timestamp of the message.
        last_sentence (str): The last sentence of the message.
        done (bool): Indicates if the message is the final one.
        context (str | None): The context of the message.
        info (ModelChatResponseInfo | None): Additional information about the response.
    """

    parent_id: str
    id: str
    children_ids: list[str]
    role: str
    content: str
    model: str
    model_name: str
    user_context: str | None
    timestamp: int
    last_sentence: str
    done: bool
    context: str | None
    info: ModelChatResponseInfo | None

    def __init__(
        self,
        parent_id: str,
        message_id: str,
        children_ids: list[str],
        role: str,
        content: str,
        model: str,
        model_name: str,
        user_context: str | None,
        timestamp: int,
        last_sentence: str,
        done: bool,
        context: str | None,
        info: ModelChatResponseInfo | None,
    ):
        self.parent_id = parent_id
        self.id = message_id
        self.children_ids = children_ids
        self.role = role
        self.content = content
        self.model = model
        self.model_name = model_name
        self.user_context = user_context
        self.timestamp = timestamp
        self.last_sentance = last_sentence
        self.done = done
        self.context = context
        self.info = info

    def to_dict(self, is_new: bool = False):
        """
        Converts the instance attributes to a dictionary, with optional modifications.

        Args:
            is_new (bool): If True, certain keys will be removed from the resulting dictionary.

        Returns:
            dict: A dictionary representation of the instance with keys formatted correctly and
                  child objects converted to dictionaries.

        Notes:
            - Keys with underscores will have the underscore removed and the following
              character capitalized.
            - If `is_new` is True, the keys 'done', 'context', 'info', and 'lastSentance'
              will be removed.
            - Ensures 'userContext' is properly renamed from 'user_context' if it exists.
        """
        chat_dict = self.__dict__.copy()
        # convert the var names to the correct format
        for key, value in chat_dict.items():
            if "_" in key:
                # delete the underscore and capitalize only the first character after it
                new_key = key.split("_", 1)[0] + "".join(
                    word.capitalize() if i == 0 else word
                    for i, word in enumerate(key.split("_")[1:])
                )
                chat_dict[new_key] = value
                del chat_dict[key]

        # convert the child objects to a dictionary
        if self.info:
            chat_dict["info"] = self.info.to_dict()

        if is_new:
            chat_dict.pop("done", None)
            chat_dict.pop("context", None)
            chat_dict.pop("info", None)
            chat_dict.pop("lastSentance", None)

        # Ensure userContext is properly renamed
        if "userContext" not in chat_dict and "user_context" in self.__dict__:
            chat_dict["userContext"] = self.__dict__["user_context"]
            del chat_dict["user_context"]

        return chat_dict
