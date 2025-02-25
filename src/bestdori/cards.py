import asyncio

from API.api import AsyncAPIClient

class Card():
    def __init__(self, card_info):
        self.id = card_info["costumeId"]
        self.thumb_id = self.id // 50
        self.resName = card_info["resourceSetName"]
        self.sdName = card_info["sdResourceName"]

    async def get_full_image(self, isTrain: bool) -> str:
        # 完整图
        card_type = "after_training" if isTrain else "normal"
        return f'https://bestdori.com/assets/jp/characters/resourceset/{self.resName}_rip/card_{card_type}.png'
    
    async def get_character_image(self, isTrain: bool) -> str:
        # 无背景图
        card_type = "after_training" if isTrain else "normal"
        return f'https://bestdori.com/assets/jp/characters/resourceset/{self.resName}_rip/trim_{card_type}.png'
    
    async def get_thumb_image(self, isTrain: bool) -> str:
        # 缩略图
        card_type = "after_training" if isTrain else "normal"
        return f'https://bestdori.com/assets/jp/thumb/chara/card{self.thumb_id:05d}_rip/{self.resName}_{card_type}.png'
    
    async def get_livesd(self) -> str:
        # live服装
        return f'https://bestdori.com/assets/jp/characters/livesd/{self.sdName}_rip/sdchara.png'
        
async def get_card(id):
    client = AsyncAPIClient("https://bestdori.com", "api.json")
    card_info = await client.fetch(client.api_endpoints["cards"]["info"].format(id=id))
    card = Card(card_info)
    return card

