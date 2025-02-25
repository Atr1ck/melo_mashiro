from melobot import Bot, PluginPlanner
from melobot.protocols.onebot.v11 import ForwardWebSocketIO, OneBotV11Protocol
from plugins.test import test

test_plugin = PluginPlanner(version="1.0.0", flows=[test])

if __name__ == "__main__":
    (
        Bot(__name__)
        .add_protocol(OneBotV11Protocol(ForwardWebSocketIO("ws://127.0.0.1:3001")))
        .load_plugin(test_plugin)
        .run()
    )