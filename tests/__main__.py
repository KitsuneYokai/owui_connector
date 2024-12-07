from typing import Any, AsyncGenerator

from owui_connector import OpenWebUiConnector

from scarletio import get_or_create_event_loop, sleep

CONNECTOR = OpenWebUiConnector(
    "127.0.0.1",
    "JWT_TOKEN_HERE",
    port=8080,
    is_ssl=False,
)

LOOP = get_or_create_event_loop()
CONNECTOR.connect()

CHAT_TITLE = "Test Chat"
CHAT_MODEL = "llama3.2:latest"
CHAT_CONTENT = "Test Content"

async def _chat_create():
    chat_response: AsyncGenerator[Any, Any] | dict[Any, Any] | str = (
        await CONNECTOR.chat(CHAT_TITLE, CHAT_MODEL, CHAT_CONTENT)
    )

    if not isinstance(chat_response, AsyncGenerator):
        print("Chat not found")
        return

    async for msg in chat_response:
        print(msg)

    print("Chat created")
    await _chat_delete()

async def _chat_delete():
    await CONNECTOR.delete_chat(CHAT_TITLE)
    await sleep(2)

if __name__ == "__main__":
    LOOP.run(_chat_create())
