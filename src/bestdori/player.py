import asyncio
import base64
import aiohttp
import cairosvg
import diskcache as dc
import lxml.etree as etree
from wand.image import Image as WandImage
from bestdori.API.api import AsyncAPIClient
from bestdori.cards import get_card ,Card
from bestdori.degrees import get_degree, Degree
from configparser import ConfigParser
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

config = ConfigParser()

config.read("src/config.conf")

API_PATH = config.get("Bestdori", "API_PATH")
FONTS_PATH = config.get("Fonts", "FONTS_PATH")
CACHE_PATH = config.get("Cache", "CACHE_PATH")

cache = dc.Cache(CACHE_PATH)

class Player:
    def __init__(self, data):
        # 基本信息
        self.user_id = data['data']['profile']['mainDeckUserSituations']['entries'][0]['userId'] 
        self.user_name = data['data']['profile']['userName']
        self.rank = data['data']['profile']['rank']
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
        
        # 称号情况
        self.degrees = []
        for degree in data['data']['profile']['userProfileDegreeMap']['entries'].values():
            self.degrees.append(degree["degreeId"])
        
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
        cards = [await get_card(card['situation_id'], card['illust']) for card in transform_cards(self.main_deck_user_situations)]
        card_images = await create_cards(cards)

        avatar_card = await get_card(self.avatar["situationId"], self.avatar['illust'])
        avatar_url = avatar_card.get_character_image()
        avatar = await fetch_and_resize(avatar_url,(800, 800))
 
        degrees = [await get_degree(degreeId) for degreeId in self.degrees]
        degrees_images = await create_degrees_overlay(degrees)

        background = create_background()
        background.paste(avatar, (-50, -50), avatar)

        info_box = create_info_box(self.user_name, self.rank, self.introduction, degrees_images, card_images)
        background.paste(info_box, (550, 100), info_box)

        # 把 Image 转换为 BytesIO
        img_bytes = BytesIO()
        background.save(img_bytes, format="PNG")  # 指定格式
        img_bytes.seek(0)  # 重要：重置指针，确保数据从头开始读取

        base64_str = f"base64://{base64.b64encode(img_bytes.getvalue()).decode("utf-8")}"
        return base64_str

async def download_image(url):
    """异步下载图片，支持 SVG 转换和本地缓存"""

    # 检查缓存中是否存在该 URL 的图片
    if url in cache:
        print(f"从缓存中读取图片: {url}")
        return Image.open(BytesIO(cache[url])).convert("RGBA")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()

                if url.endswith(".svg"):
                    # 将 SVG 转换为 PNG
                    png_data = cairosvg.svg2png(bytestring=content)
                    image_data = png_data
                else:
                    image_data = content

                # 将图片数据保存到缓存
                cache[url] = image_data
                print(f"图片已缓存: {url}")

                return Image.open(BytesIO(image_data)).convert("RGBA")
            else:
                raise Exception(f"无法下载图片: {url}, 状态码: {response.status}")

def transform_cards(cards):
    n = len(cards)
    result = [None] * n  # 先创建一个占位的新数组
    index = (n - 1) // 2  # 计算初始中心位置
    step = 1  # 记录扩展的步长
    result[index] = cards[0]

    for num in range(index):
        result[index - step] = cards[2 * num + 1]
        result[index + step] = cards[2 * num + 2]
        step += 1
    return result

async def create_degrees_overlay(degrees: list[Degree]) -> list[Image]:
    """创建带称号和活动排名图标的叠加层"""
    degree_images = []

    for degree in degrees:
        degree_image = await download_image(degree.get_event())
        degree_image = degree_image.resize((175, 40))
        if degree.degreeType == "event_point":
            rank = await fetch_and_resize(degree.get_rank(), (175, 40))
            icon = await fetch_and_resize(degree.get_icon(), (40, 40))
            degree_image.paste(rank, (0, 0), rank)
            degree_image.paste(icon, (0, 0), icon)
        
        degree_images.append(degree_image)
    
    return degree_images

def text_x_center(text: str, box: Image, font:ImageFont):
    draw = ImageDraw.Draw(box)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]  # 计算文本宽度

    # 计算水平居中的 x 坐标
    x_center = (box.width - text_width) // 2
    return x_center

def create_background() -> Image:
    """创建背景图"""
    background = Image.new("RGBA", (1200, 800), "white")
    background_img = Image.open("image.png").resize((1200, 800))
    background.paste(background_img, (0, 0))
    return background

def create_info_box(user_name: str, rank: int, introduction: str, degrees: list[Image], card_images: list[Image]) -> Image:
    """创建玩家信息框"""
    info_box = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(info_box)
    
    name_font = ImageFont.truetype(FONTS_PATH, 30)
    rank_font = ImageFont.truetype(FONTS_PATH, 20)
    intro_font = ImageFont.truetype(FONTS_PATH, 20)

    draw.text((text_x_center(user_name, info_box, name_font), 10), user_name, fill="black", font=name_font)
    rank_text = f"等级：{rank}"
    draw.text((text_x_center(rank_text, info_box, rank_font), 50), rank_text, fill="black", font=rank_font)
    draw.text((text_x_center(introduction, info_box, intro_font), 80), introduction, fill="gray", font=intro_font)


    start_x = (info_box.width - 175) // 2 if len(degrees) == 1 else (info_box.width - (175 + 50) * len(degrees)) // 2
    start_y = 150
    for i, degree in enumerate(degrees):
        info_box.paste(degree, (start_x + i * (175 + 50), 150), degree)

    # 乐队卡片（底部对齐）
    card_width, card_height = 100, 100
    start_x = (info_box.width - (card_width + 10) * len(card_images)) // 2
    start_y = 400
    for i, card in enumerate(card_images):
        info_box.paste(card, (start_x + i * (card_width + 10), start_y), card)

    return info_box

async def create_cards(cards: list[Card]) -> list[Image]:
    card_images = []
    for card in cards:
        card_image = await fetch_and_resize(card.get_thumb_image(), (100, 100))
        star = await fetch_and_resize(card.get_star(), (14, 14))
        attr = await fetch_and_resize(card.get_attribute(), (28, 28))
        band = await fetch_and_resize(card.get_band(), ((30, 30)))
        thumb_frame = await fetch_and_resize(card.get_thumb_frame(), (100, 100))
        
        card_image.paste(thumb_frame, (0, 0), thumb_frame)
        for count in range(0, card.rarity):
            step = 13
            card_image.paste(star, (4, 95 - step * (count + 1)), star)
        card_image.paste(band, (0, 0), band)
        card_image.paste(attr, (72, 0), attr)
        card_images.append(card_image)

    return card_images

async def fetch_and_resize(image_url: str, size: tuple[int, int]):
    """下载图片并调整大小"""
    image = await download_image(image_url)  # 直接下载
    return image.resize(size)  # 调整大小

async def get_player(id):
    client = AsyncAPIClient("https://bestdori.com", API_PATH, CACHE_PATH)
    api_url = client.api_endpoints["player"]["info"].format(server="cn", id=id)
    player_info = await client.fetch(api_url, cache=False)
    if player_info["data"]["profile"] == None:
        client.delete_cache(api_url)
        print("数据无效，已删除")
        return "Unvalid Data"
    player = Player(player_info)
    return player
