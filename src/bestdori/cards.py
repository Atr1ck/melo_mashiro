import asyncio

from bestdori.API.api import AsyncAPIClient
from configparser import ConfigParser

config = ConfigParser()

config.read("src/config.conf")

API_PATH = config.get("Bestdori", "API_PATH")
CACHE_PATH = config.get("Cache", "CACHE_PATH")

class Card():
    def __init__(self, card_info, id, illust):
        self.id = id
        self.illust = illust
        self.thumb_id = self.id // 50
        self.resName = card_info["resourceSetName"]
        self.sdName = card_info["sdResourceName"]
        self.rarity = card_info["rarity"]
        self.attr = card_info["attribute"]
        self.charaId = card_info["characterId"]
        self.bandId = (self.charaId - 1) // 5 + 1

    def get_full_image(self) -> str:
        # 完整图
        return f'https://bestdori.com/assets/cn/characters/resourceset/{self.resName}_rip/card_{self.illust}.png'
    
    def get_character_image(self) -> str:
        # 无背景图
        return f'https://bestdori.com/assets/cn/characters/resourceset/{self.resName}_rip/trim_{self.illust}.png'
    
    def get_thumb_image(self) -> str:
        # 缩略图
        return f'https://bestdori.com/assets/cn/thumb/chara/card{self.thumb_id:05d}_rip/{self.resName}_{self.illust}.png'
    
    def get_livesd(self) -> str:
        # live服装
        return f'https://bestdori.com/assets/cn/characters/livesd/{self.sdName}_rip/sdchara.png'
    
    def get_thumb_frame(self) -> str:
        # 缩略图边框
        if self.rarity >= 2:
            return f'https://bestdori.com/res/image/card-{self.rarity}.png'
        else:
            return f'https://bestdori.com/res/image/card-{self.rarity}-{self.attr}.png'

    def get_frame(self) -> str:
        # 卡面边框
        return f'https://bestdori.com/res/image/frame-{self.rarity}.png'
    
    def get_star(self) -> str:
        star_type = "_trained" if self.illust == "after_training" else ""
        star_url = f"https://bestdori.com/res/icon/star{star_type}.png"
        return star_url
        
    def get_attribute(self):
        attr_url = f"https://bestdori.com/res/icon/{self.attr}.svg"
        return attr_url
    
    def get_band(self):
        return f'https://bestdori.com/res/icon/band_{self.bandId}.svg'

async def get_card(id, illust):
    client = AsyncAPIClient("https://bestdori.com", API_PATH, CACHE_PATH)
    card_info = await client.fetch(client.api_endpoints["cards"]["info"].format(id=id))
    card = Card(card_info, id, illust)
    return card

