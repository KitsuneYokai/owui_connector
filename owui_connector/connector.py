"""
Connector to OpenWebUi
"""

from datetime import datetime
from typing import Any, AsyncGenerator, Literal
from uuid import uuid4

from scarletio import get_or_create_event_loop
from scarletio.http_client.client_response import ClientResponse

from .api_requests import ApiRequests
from .models import (
    Chat,
    ChatReference,
    MessageRoles,
    ModelChatResponse,
    OllamaRequest,
    UserChatMessage,
    ModelChatResponseInfo,
)


class OpenWebUiConnector:
    api: ApiRequests

    def __init__(self, host: str, token: str, port: int = 8080, is_ssl: bool = False):
        self.host = host
        self.port = port
        self.api = ApiRequests(token, host, port, is_ssl)

    def connect(self):
        get_or_create_event_loop().run(self.api.connect())

    async def delete_chat(self, chat_title: str = "", chat_id: str = ""):
        if not chat_title and not chat_id:
            return "No chat id or title provided"

        if chat_id and chat_title:
            return "Provide only chat id or title"

        if chat_id:
            chat = await self.api.get_chat_by_id(chat_id)
            if not chat:
                return "Chat not found"

            return await self.api.delete_chat_by_id(chat["id"])

        if chat_title:
            return await self.api.delete_chat_by_title(chat_title)

    async def chat(
        self,
        chat_title: str,
        model: str,
        content: str,
        stream: bool = True,
    ):
        chat = await self.api.get_chat_by_title(chat_title)
        if not chat:
            # we want to create a chat
            return await self.create_chat(chat_title, model, content, stream)

        return await self.respond_to_chat(chat_title, content, model, stream)

    async def create_chat(
        self,
        chat_title: str,
        model: str,
        content: str,
        stream: bool = True,
    ) -> AsyncGenerator[Any, Any] | dict[Any, Any]:
        user_msg_id = str(uuid4())
        model_msg_id = str(uuid4())
        current_timestamp: int = int(datetime.now().timestamp())
        chat_reference = ChatReference(
            chat_id="",
            title=str(chat_title),
            models=[model],
            params={},
            messages=[
                UserChatMessage(
                    message_id=user_msg_id,
                    parent_id=None,
                    children_ids=[model_msg_id],
                    role=MessageRoles.USER.value,
                    content=content,
                    timestamp=current_timestamp,
                    models=[model],
                ),
                ModelChatResponse(
                    parent_id=user_msg_id,
                    message_id=model_msg_id,
                    children_ids=[],
                    role=MessageRoles.ASSISTENT.value,
                    content="",
                    model=model,
                    model_name=model,
                    user_context=None,
                    timestamp=current_timestamp,
                    last_sentence="",
                    done=False,
                    context=None,
                    info=None,
                ),
            ],
            history=None,
            tags=[],
            timestamp=current_timestamp,
        )

        chat = Chat(
            chat=chat_reference,
        )

        chat_request: ClientResponse = await self.api.create_chat(chat)
        chat_request_json: dict | None = await chat_request.json()

        if not chat_request_json or not chat_request_json["id"]:
            raise RuntimeError("Could not create chat!")

        chat_reference.id = chat_request_json["id"]

        # build the ollama request body
        ollama_request = OllamaRequest(
            stream=stream,
            model=model,
            messages=[
                {
                    "role": MessageRoles.USER.value,
                    "content": content,
                },
            ],
            options={},
            chat_id=chat_reference.id,
            request_id=str(uuid4()),
        )

        # lets do the request
        response = await self.api.send_ollama_request(
            ollama_request, chat_reference, stream=stream
        )

        if stream:
            return response

        return response

    async def respond_to_chat(
        self,
        chat_title: str,
        content: str,
        model: str,
        stream: bool = True,
    ):
        chat = await self.api.get_chat_by_title(chat_title)
        if not chat:
            raise ValueError("Chat not found")

        user_msg_id = str(uuid4())
        model_msg_id = str(uuid4())
        current_timestamp: int = int(datetime.now().timestamp())

        messages: list[ModelChatResponse | UserChatMessage] = []

        for message in chat["chat"]["messages"]:
            print(message)
            if message["role"] == MessageRoles.USER.value:
                messages.append(
                    UserChatMessage(
                        message_id=message["id"],
                        parent_id=message["parentId"],
                        children_ids=message["childrenIds"],
                        role=message["role"],
                        content=message["content"],
                        timestamp=message["timestamp"],
                        models=[model],
                    )
                )
            elif message["role"] == MessageRoles.ASSISTENT.value:
                print("-------------------")
                print(message)
                print("-------------------")
                messages.append(
                    ModelChatResponse(
                        parent_id=message["parentId"],
                        message_id=message["id"],
                        children_ids=message["childrenIds"],
                        role=message["role"],
                        content=message["content"],
                        model=message["model"],
                        model_name=message["modelName"],
                        user_context=message["userContext"],
                        timestamp=message["timestamp"],
                        last_sentence=(
                            message["lastSentance"] if "lastSentance" in message else ""
                        ),
                        done=message["done"],
                        context=message["context"],
                        info=ModelChatResponseInfo(
                            total_duration=message["info"].get("total_duration", 0),
                            load_duration=message["info"].get("load_duration", 0),
                            prompt_eval_count=message["info"].get(
                                "prompt_eval_count", 0
                            ),
                            prompt_eval_duration=message["info"].get(
                                "prompt_eval_duration", 0
                            ),
                            eval_count=message["info"].get("eval_count", 0),
                            eval_duration=message["info"].get("eval_duration", 0),
                        ),
                    )
                )

        messages.sort(key=lambda msg: msg.timestamp)

        chat_reference = ChatReference(
            chat_id=chat["id"],
            title=str(chat_title),
            models=[model],
            params={},
            messages=[
                *messages,
                UserChatMessage(
                    message_id=user_msg_id,
                    parent_id=messages[-1].id,
                    children_ids=[model_msg_id],
                    role=MessageRoles.USER.value,
                    content=content,
                    timestamp=current_timestamp,
                    models=[model],
                ),
                ModelChatResponse(
                    parent_id=user_msg_id,
                    message_id=model_msg_id,
                    children_ids=[],
                    role=MessageRoles.ASSISTENT.value,
                    content="",
                    model=model,
                    model_name=model,
                    user_context=None,
                    timestamp=current_timestamp,
                    last_sentence="",
                    done=False,
                    context=None,
                    info=None,
                ),
            ],
            history=None,
            tags=[],
            timestamp=current_timestamp,
        )

        # lets do the ollama request
        ollama_messages = []
        for message in chat_reference.messages:
            if isinstance(message, UserChatMessage):
                ollama_messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

            if isinstance(message, ModelChatResponse):
                ollama_messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )
        ollama_request = OllamaRequest(
            stream=stream,
            model=model,
            messages=[
                *ollama_messages,
                {
                    "role": MessageRoles.USER.value,
                    "content": content,
                },
            ],
            options={},
            chat_id=chat_reference.id,
            request_id=str(uuid4()),
        )

        # lets do the request
        response = await self.api.send_ollama_request(
            ollama_request, chat_reference, stream=stream
        )

        if stream:
            return response

        return response
