from melobot import send_text, on_start_match
from melobot.protocols.onebot.v11 import MessageEvent, on_message

@on_start_match(".sayhi")
async def test() -> None:
    await send_text("Hello, melobot!")