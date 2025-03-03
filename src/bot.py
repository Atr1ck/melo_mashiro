import cairosvg
from melobot import Bot, PluginPlanner
from melobot.protocols.onebot.v11 import ForwardWebSocketIO, OneBotV11Protocol, Adapter
from configparser import ConfigParser
from plugins.bandori import bandori_cards, bandori_player
from lxml import etree

# 强制cairosvg使用lxml
cairosvg.parser.NODE_PARSER = etree.XMLParser(resolve_entities=False, no_network=True)

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
    bot.run(debug=True)   