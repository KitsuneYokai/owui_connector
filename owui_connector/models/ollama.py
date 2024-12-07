from typing import Any


class OllamaRequest:
    """
    OllamaRequest represents a request to the Ollama API.

    Attributes:
        stream (bool): Indicates whether the response should be streamed.
        model (str): The model to be used for the request.
        messages (list[dict[str, Any]]): A list of message dictionaries containing the
        conversation history.
        options (dict[str, Any]): Additional options for the request.
        session_id (str): The session identifier.
        chat_id (str): The chat identifier.
        id (str): The unique identifier for the request.
    """

    stream: bool
    model: str
    messages: list[dict[str, Any]]
    options: dict[str, Any]
    session_id: str | None
    chat_id: str
    id: str

    def __init__(
        self,
        request_id: str,
        stream: bool,
        model: str,
        messages: list[dict[str, Any]],
        options: dict[str, Any],
        chat_id: str,
        session_id: str | None = None,
    ):
        self.stream = stream
        self.model = model
        self.messages = messages
        self.options = options
        self.session_id = session_id
        self.chat_id = chat_id
        self.id = request_id
