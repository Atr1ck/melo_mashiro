import asyncio
from API.api import  AsyncAPIClient

class Player:
    def __init__(self, data):
        # 基本信息
        self.user_id = data['data']['profile']['userId'] 
        self.user_name = data['data']['profile']['userName']
        self.rank = data['data']['profile']['rank']
        self.degree = data['data']['profile']['degree']
        self.introduction = data['data']['profile']['introduction']
        
        # 主乐队情况
        self.main_deck_user_situations = []
        for situation in data['data']['profile']['mainDeckUserSituations']['entries']:
            self.main_deck_user_situations.append({
                'situation_id': situation['situationId'],
                'illust' : situation['illust']
            })
        
        # 区域道具
        self.enabled_user_area_items = []
        for item in data['data']['profile']['enabledUserAreaItems']['entries']:
            self.enabled_user_area_items.append({
                'area_item_id': item['areaItemId'],
                'category': item['areaItemCategory'],
                'level': item['level']
            })

async def get_player(id):
    client = AsyncAPIClient("https://bestdori.com", "api.json")
    player_info = await client.fetch(client.api_endpoints["player"]["info"].format(server="cn", id=id))
    player = Player(player_info)
    return player
