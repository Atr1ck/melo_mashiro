from melobot import Bot, PluginPlanner
from melobot.protocols.onebot.v11 import ForwardWebSocketIO, OneBotV11Protocol, Adapter
from configparser import ConfigParser
from plugins.bandori import bandori_cards, bandori_player

config = ConfigParser()

config.read("src/config.conf")

plugin = PluginPlanner(version="1.0.0", flows=[bandori_cards, bandori_player])

if __name__ == "__main__":
    bot = (
        Bot(
            "Mashiro"
        )
        .add_protocol(OneBotV11Protocol(ForwardWebSocketIO("ws://127.0.0.1:3001")))
    )
    bot.load_plugins([plugin])
    bot.run()   