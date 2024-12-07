"""
This file holds the model for a completed chat Request object.
This object is being send as a dictionary to the client, when the ollama
response is received and the chat is completed.
"""

from .. import MessageRoles


class CompletedUserMessage:
    id: str
    role: MessageRoles = MessageRoles.USER
    content: str
    timestamp: int

    def __init__(self, id: str, content: str, timestamp: int):
        self.id = id
        self.content = content
        self.timestamp = timestamp


class CompletedModelMessageInfo:
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


class CompletedModelMessage:
    id: str
    role: MessageRoles = MessageRoles.ASSISTENT
    content: str
    info: CompletedModelMessageInfo | dict[str, int]
    timestamp: int

    def __init__(
        self,
        id: str,
        content: str,
        info: CompletedModelMessageInfo | dict[str, int],
        timestamp: int,
    ):
        self.id = id
        self.content = content
        self.info = info
        self.timestamp = timestamp


class CompletedRequest:
    model: str
    messages: list[CompletedUserMessage | CompletedModelMessage]
    chat_id: str
    session_id: str
    id: str

    def __init__(
        self,
        model: str,
        messages: list[CompletedUserMessage | CompletedModelMessage],
        chat_id: str,
        session_id: str,
        id: str,
    ):
        self.model = model
        self.messages = messages
        self.chat_id = chat_id
        self.session_id = session_id
        self.id = id
