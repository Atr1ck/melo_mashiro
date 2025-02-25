import base64
import requests
from bestdori.API.api import AsyncAPIClient
from bestdori.cards import get_card
from configparser import ConfigParser
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

config = ConfigParser()

config.read("src/config.conf")

API_PATH = config.get("Bestdori", "API_PATH")

class Player:
    def __init__(self, data):
        # 基本信息
        self.user_id = data['data']['profile']['mainDeckUserSituations']['entries'][0]['userId'] 
        self.user_name = data['data']['profile']['userName']
        self.rank = data['data']['profile']['rank']
        self.degree = data['data']['profile']['degree']
        self.introduction = data['data']['profile']['introduction']
        try:
            self.avatar = { 
                "situationId" : data['data']['profile']['userProfileSituation']['situationId'],
                "illust" : data['data']['profile']['userProfileSituation']['illust']
            }
        except:
            self.avatar = { 
                "situationId" : data['data']['profile']['mainDeckUserSituations']['entries'][0]['situationId'] ,
                "illust" : data['data']['profile']['mainDeckUserSituations']['entries'][0]['illust']
            }
        # 主乐队情况
        self.main_deck_user_situations = []
        for situation in data['data']['profile']['mainDeckUserSituations']['entries']:
            self.main_deck_user_situations.append({
                'situation_id': situation['situationId'],
                'illust' : situation['illust']
            })
        
        # 区域道具
        try:
            self.enabled_user_area_items = []
            for item in data['data']['profile']['enabledUserAreaItems']['entries']:
                self.enabled_user_area_items.append({
                    'area_item_id': item['areaItemId'],
                    'category': item['areaItemCategory'],
                    'level': item['level']
                })
        except:
            pass
            
    async def player_dataImg(self) -> Image:
        cards_url = []
        for card_info in self.main_deck_user_situations:
            card = await get_card(card_info["situation_id"])
            cards_url.append(await card.get_thumb_image(card_info["illust"]))

        avatar_card = await get_card(self.avatar["situationId"])
        avatar_url = await avatar_card.get_character_image(card_info["illust"])

        avatar = await download_image(avatar_url)
        card_images = [await download_image(url) for url in cards_url]

        # 创建背景
        background = Image.new("RGBA", (1200, 800), "white")

        # 头像居中
        avatar_size = (500, 500)
        avatar = avatar.resize(avatar_size)
        avatar_x = (background.width - avatar_size[0]) // 2
        avatar_y = 150
        background.paste(avatar, (avatar_x, avatar_y), avatar)

        # 玩家信息框
        info_box = Image.new("RGBA", (300, 150), "white")
        draw = ImageDraw.Draw(info_box)
        font_path = "/usr/share/fonts/adobe-source-han-sans/SourceHanSansCN-Normal.otf"
        font = ImageFont.truetype(font_path, 40)

        # 绘制玩家信息
        draw.text((10, 10), self.user_name, fill="black", font=font)
        draw.text((10, 40), str(self.rank), fill="black", font=font)
        draw.text((10, 120), self.introduction, fill="gray", font=font)

        # 设置信息框位置
        info_x = avatar_x + avatar_size[0] + 50
        info_y = avatar_y + 50
        background.paste(info_box, (info_x, info_y))

        # 乐队卡片（底部对齐）
        card_width, card_height = 150, 150
        start_x = (background.width - (card_width + 10) * len(card_images)) // 2  # 居中排列
        start_y = 600
        for i, card in enumerate(card_images):
            resized_card = card.resize((card_width, card_height))
            background.paste(resized_card, (start_x + i * (card_width + 10), start_y), resized_card)

        # 把 Image 转换为 BytesIO
        img_bytes = BytesIO()
        background.save(img_bytes, format="PNG")  # 指定格式
        img_bytes.seek(0)  # 重要：重置指针，确保数据从头开始读取

        base64_str = f"base64://{base64.b64encode(img_bytes.getvalue()).decode("utf-8")}"
        return base64_str

async def download_image(url):
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content)).convert("RGBA")
    else:
        raise Exception(f"无法下载图片: {url}")

async def get_player(id):
    client = AsyncAPIClient("https://bestdori.com", API_PATH)
    player_info = await client.fetch(client.api_endpoints["player"]["info"].format(server="cn", id=id))
    player = Player(player_info)
    return player
