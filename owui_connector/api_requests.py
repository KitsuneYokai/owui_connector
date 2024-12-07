"""
This File houses the HTTP Operations for the OWUI Connector
"""

from json import dumps
from uuid import uuid4

from scarletio import get_or_create_event_loop, from_json
from scarletio.http_client import HTTPClient
from scarletio.web_socket import WebSocketClient
from scarletio.web_common import ConnectionClosed
from scarletio.http_client.client_response import ClientResponse

from .models import (
    Chat,
    ChatReference,
    ModelChatResponse,
    OllamaRequest,
    User,
    UserChatMessage,
    WeekChatReference,
    CompletedRequest,
    CompletedUserMessage,
    CompletedModelMessage,
    CompletedModelMessageInfo,
    ModelChatResponseInfo,
)


class ApiRequests:
    http_client: HTTPClient
    api_user: User

    base_url: str
    token: str
    is_ssl: bool
    session_id: str = ""
    transport_id: str
    ws_connection: WebSocketClient

    def __init__(
        self,
        token: str,
        host: str,
        port: int = 8080,
        is_ssl: bool = False,
    ):
        self.http_client = HTTPClient(get_or_create_event_loop())

        self.base_url = f"http{'s' if is_ssl else ''}://{host}:{port}"
        self.ws_url = f"ws{'s' if is_ssl else ''}://{host}:{port}"
        self.token = token
        self.is_ssl = is_ssl
        self.transport_id = str(uuid4())

    async def connect(self):
        # get the session id and the user
        self.session_id = await self.get_session_id()
        self.api_user: User = await self.get_panel_user()

        # auth the session id so we can start using the api
        await self.auth_session()

        # lets start the websocket connection
        async with self.http_client.connect_web_socket(
            f"{self.ws_url}/ws/socket.io/?EIO=4&transport=websocket&sid={self.session_id}",
        ) as websocket:
            if not websocket:
                raise ConnectionError("Failed to connect to the OpenWebUi panel")

            self.ws_connection = websocket

            try:
                await websocket.ensure_open()
                # send 2probe to the server
                await websocket.send("2probe")

            except ConnectionClosed:
                # TODO: Implement reconnect logic
                print("OpenWebUI Connector - Websocket Connection closed")

            while True:
                message = await websocket.receive()

                if message == "3probe":
                    await websocket.send("5")
                    break

                if message == "2":
                    await websocket.send("3")
                    break

                print(f"OpenWebUI Connector - Unhandled Websocket event: {message}")

    async def get_session_id(self) -> str:
        response: ClientResponse | None = await self.http_client.get(
            f"{self.base_url}/ws/socket.io/?EIO=4&transport=polling&t={self.transport_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if not isinstance(response, ClientResponse) or response.status != 200:
            raise ConnectionError("Failed to connect to the OpenWebUi panel")

        response = await response.text()
        response_json = from_json(str(response).replace("0", ""))

        return str(response_json["sid"])

    async def get_panel_user(self) -> User:
        response: ClientResponse | None = await self.http_client.get(
            f"{self.base_url}/api/v1/auths/",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if not isinstance(response, ClientResponse) or response.status != 200:
            raise ConnectionError(
                "Failed to get the panel user. \
                Maybe the token is invalid, or the panel is unreachable?"
            )

        response_json = await response.json()
        if not isinstance(response_json, dict):
            raise ConnectionError(
                "Failed to get the panel user. The response is not a dictionary."
            )

        user = User(
            response_json["id"],
            response_json["email"],
            response_json["name"],
            response_json["role"],
            response_json["profile_image_url"],
        )

        return user

    async def get_week_chats(self) -> list[WeekChatReference]:
        response: ClientResponse | None = await self.http_client.get(
            f"{self.base_url}/api/v1/chats/",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if not isinstance(response, ClientResponse) or response.status != 200:
            raise ConnectionError(
                "Failed to get the week chats.\
                Maybe the token is invalid, or the panel is unreachable?"
            )

        response_json = await response.json()

        if not isinstance(response_json, list):
            raise ConnectionError(
                "Failed to get the week chats. The response is not a list."
            )
        print("Week Chats")
        print(response_json)
        week_chats = [
            WeekChatReference(
                chat["id"],
                chat["title"],
                chat["updated_at"],
                chat["created_at"],
            )
            for chat in response_json
        ]
        return week_chats

    async def get_chat_by_id(self, chat_id: str) -> dict:
        response: ClientResponse | None = await self.http_client.get(
            f"{self.base_url}/api/v1/chats/{chat_id}/",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if not isinstance(response, ClientResponse) or response.status != 200:
            raise ConnectionError(
                "Failed to get the week chat.\
                Maybe the token is invalid, or the panel is unreachable?"
            )

        response_json = await response.json()

        if not isinstance(response_json, dict):
            raise ConnectionError(
                "Failed to get the week chat. The response is not a dictionary."
            )

        return response_json

    async def get_chat_by_title(self, chat_title: str) -> dict | None:
        week_chats = await self.get_week_chats()
        chat = next((chat for chat in week_chats if chat.title == chat_title), None)

        if not isinstance(chat, WeekChatReference):
            return None

        return await self.get_chat_by_id(chat.id)

    async def auth_session(self) -> ClientResponse:
        response: ClientResponse | None = await self.http_client.post(
            f"{self.base_url}/ws/socket.io/?EIO=4&transport=polling&t={self.transport_id}&sid={self.session_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            data='40{"token":"' + self.token + '"}',
        )
        print(response)
        if not isinstance(response, ClientResponse) or response.status != 200:
            raise ConnectionError(
                "Failed to authenticate the session.\
                Maybe the token is invalid, or the panel is unreachable?"
            )

        return response

    async def create_chat(self, chat: Chat) -> ClientResponse:
        chat_json = chat.to_dict(is_new=True)

        response: ClientResponse | None = await self.http_client.post(
            f"{self.base_url}/api/v1/chats/new",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
            },
            data=dumps(chat_json),
        )

        if not isinstance(response, ClientResponse) or response.status != 200:
            raise ConnectionError(
                "Failed to create the chat.\
                Maybe the token is invalid, or the panel is unreachable?"
            )

        return response

    async def delete_chat_by_id(self, chat_id: str) -> ClientResponse:
        response: ClientResponse | None = await self.http_client.delete(
            f"{self.base_url}/api/v1/chats/{chat_id}/",
            headers={"Authorization": f"Bearer {self.token}"},
        )

        if not isinstance(response, ClientResponse) or response.status != 200:
            raise ConnectionError(
                "Failed to delete the chat.\
                Maybe the token is invalid, or the panel is unreachable?"
            )

        return response

    async def delete_chat_by_title(self, chat_title: str) -> ClientResponse:
        chat = await self.get_chat_by_title(chat_title)
        if not chat:
            raise ValueError("Chat not found")

        return await self.delete_chat_by_id(chat["chat"]["id"])

    async def send_ollama_request(
        self,
        ollama_request: OllamaRequest,
        chat_reference: ChatReference,
        stream: bool = True,
    ):
        # if we got stream true we need to return an async generator
        if stream:
            return self._stream_response_generator(ollama_request, chat_reference)

        if self.http_client is None:
            raise ValueError("Http client not initialized")

        # if we got stream false we need to return the response
        async with self.http_client.post(
            f"{self.base_url}/ollama/api/chat",
            data=dumps(ollama_request.__dict__),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response and response.status != 200 or not response:
                raise ConnectionError("Failed to create chat on the OpenWebUi panel")

            response_content = await response.json()
            complete_model_message_info = CompletedModelMessageInfo(
                total_duration=response_content["total_duration"],
                load_duration=response_content["load_duration"],
                prompt_eval_count=response_content["prompt_eval_count"],
                prompt_eval_duration=response_content["prompt_eval_duration"],
                eval_count=response_content["eval_count"],
                eval_duration=response_content["eval_duration"],
            )

            response_content = response_content["message"]["content"]

            response = await response.json()

            # check if is type dict
            if not isinstance(response, dict):
                raise ConnectionError("Ollama returned an invalid response")

            await self._send_chat_completion(
                response_content,
                complete_model_message_info,
                chat_reference,
                ollama_request.id,
            )
            return response

    async def _stream_response_generator(
        self,
        data: OllamaRequest,
        chat_reference: ChatReference,
    ):
        """
        This internal function is used to create an async generator that streams the response.
        """
        if self.http_client is None:
            raise ValueError("Http client not initialized")

        async with self.http_client.post(
            f"{self.base_url}/ollama/api/chat",
            data=dumps(data.__dict__),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        ) as response:

            if response and response.status != 200 or not response:
                raise ConnectionError("Failed to create chat on the OpenWebUi panel")

            response_content = ""

            complete_model_message_info = CompletedModelMessageInfo(
                total_duration=0,
                load_duration=0,
                prompt_eval_count=0,
                prompt_eval_duration=0,
                eval_count=0,
                eval_duration=0,
            )

            payload_stream = response.payload_stream

            payload_stream.add_done_callback(
                lambda _: get_or_create_event_loop().ensure_future(
                    self._send_chat_completion(
                        response_content,
                        complete_model_message_info,
                        chat_reference,
                        data.id,
                    )
                )
            )

            if payload_stream is not None:
                async for chunk in payload_stream:
                    json_content = from_json(chunk.tobytes()[:-1])

                    if json_content.get("done") is True:
                        # lets add the eval time to the info
                        complete_model_message_info.total_duration += json_content[
                            "total_duration"
                        ]
                        complete_model_message_info.load_duration += json_content[
                            "load_duration"
                        ]
                        complete_model_message_info.prompt_eval_count += json_content[
                            "prompt_eval_count"
                        ]
                        complete_model_message_info.prompt_eval_duration += (
                            json_content["prompt_eval_duration"]
                        )
                        complete_model_message_info.eval_count += json_content[
                            "eval_count"
                        ]
                        complete_model_message_info.eval_duration += json_content[
                            "eval_duration"
                        ]

                    response_content += json_content["message"]["content"]

                    yield json_content

    async def _send_chat_completion(
        self,
        response_content: str,
        complete_model_message_info: CompletedModelMessageInfo,
        chat_reference: ChatReference,
        ollama_request_id: str,
    ):
        """
        This internal function is send, immediately after the chat is completed,
        to keep the panel in sync with the wrapper.
        """
        # set the message in the chat references content to the response content
        chat_reference.messages[-1].content = response_content

        messages = []
        for message in chat_reference.messages:
            if isinstance(message, UserChatMessage):
                messages.append(
                    CompletedUserMessage(
                        id=message.id,
                        content=message.content,
                        timestamp=message.timestamp,
                    ).__dict__
                )

            if isinstance(message, ModelChatResponse):
                # if its the last message we need to add the info, otherwise, we just use the normal class
                if message == chat_reference.messages[-1]:
                    info = complete_model_message_info
                    message.info = ModelChatResponseInfo(
                        total_duration=info.total_duration,
                        load_duration=info.load_duration,
                        prompt_eval_count=info.prompt_eval_count,
                        prompt_eval_duration=info.prompt_eval_duration,
                        eval_count=info.eval_count,
                        eval_duration=info.eval_duration,
                    )

                else:
                    info = message.info

                # lets add the info to the last message

                messages.append(
                    CompletedModelMessage(
                        id=message.id,
                        content=message.content,
                        info=info.__dict__,
                        timestamp=message.timestamp,
                    ).__dict__
                )

        # lets make sure the messages are sorted by timestamp
        messages.sort(key=lambda msg: msg.get("timestamp"))

        request: CompletedRequest = CompletedRequest(
            id=ollama_request_id,
            chat_id=chat_reference.id,
            model=chat_reference.models[0],
            session_id=self.session_id,
            messages=messages,
        )

        if not self.http_client:
            raise ValueError("Http client not initialized")

        # Lets do the post request
        response = await self.http_client.post(
            f"{self.base_url}/api/chat/completed",
            data=dumps(request.__dict__),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        )

        if not isinstance(response, ClientResponse) or response.status != 200:
            raise ConnectionError(
                "Failed to send chat completion to the OpenWebUi panel"
            )

        print(await response.json())

        # update the history of the chat reference
        chat_reference.history = chat_reference.chat_messages_to_history(
            chat_reference.messages
        )

        # set every chat msg to done
        for message in chat_reference.messages:
            if isinstance(message, ModelChatResponse):
                message.done = True

        # lets post to the chat
        response = await self.http_client.post(
            f"{self.base_url}/api/v1/chats/{chat_reference.id}/",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            data=dumps(Chat(chat_reference).to_dict()),
        )

        if response and response.status != 200 or not response:
            raise ConnectionError(
                "Failed to send chat completion to the OpenWebUi panel"
            )

        print(await response.json())
