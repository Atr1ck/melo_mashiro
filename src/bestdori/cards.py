import asyncio

from bestdori.API.api import AsyncAPIClient
from configparser import ConfigParser

config = ConfigParser()

config.read("src/config.conf")

API_PATH = config.get("Bestdori", "API_PATH")

class Card():
    def __init__(self, card_info, id):
        self.id = id
        self.thumb_id = self.id // 50
        self.resName = card_info["resourceSetName"]
        self.sdName = card_info["sdResourceName"]

    async def get_full_image(self, card_type: str) -> str:
        # 完整图
        return f'https://bestdori.com/assets/cn/characters/resourceset/{self.resName}_rip/card_{card_type}.png'
    
    async def get_character_image(self, card_type: str) -> str:
        # 无背景图
        return f'https://bestdori.com/assets/cn/characters/resourceset/{self.resName}_rip/trim_{card_type}.png'
    
    async def get_thumb_image(self, card_type: str) -> str:
        # 缩略图
        return f'https://bestdori.com/assets/cn/thumb/chara/card{self.thumb_id:05d}_rip/{self.resName}_{card_type}.png'
    
    async def get_livesd(self) -> str:
        # live服装
        return f'https://bestdori.com/assets/cn/characters/livesd/{self.sdName}_rip/sdchara.png'
        
async def get_card(id):
    client = AsyncAPIClient("https://bestdori.com", API_PATH)
    card_info = await client.fetch(client.api_endpoints["cards"]["info"].format(id=id))
    card = Card(card_info, id)
    return card

