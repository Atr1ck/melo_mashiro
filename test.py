from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
import cairosvg

user_name = "我真是新手"
rank = 78
introduction = "请多多关照！"
FONTS_PATH = "src/fonts/SourceHanSansCN-Normal.otf"


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

def download_image(url):
    print(url)
    
    response = requests.get(url)

    if url.endswith(".svg"):
        # 将 SVG 转换为 PNG
        png_data = cairosvg.svg2png(bytestring=response.content)
        return Image.open(BytesIO(png_data)).convert("RGBA")
    
    if response.status_code == 200:
        return Image.open(BytesIO(response.content)).convert("RGBA")
    else:
        raise Exception(f"无法下载图片: {url}")
    
def text_x_center(text: str, box: Image, font:ImageFont):
    draw = ImageDraw.Draw(box)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]  # 计算文本宽度

    # 计算水平居中的 x 坐标
    x_center = (box.width - text_width) // 2
    return x_center

def download_and_resize_image(url: str, size: tuple[int, int]) -> Image:
    """下载并调整图片大小"""
    return download_image(url).resize(size)

def create_degrees_overlay(degrees_url: list[str], event_rank_url: str, event_icon_url: str) -> list[Image]:
    """创建带称号和活动排名图标的叠加层"""
    degrees = [download_and_resize_image(url, (175, 40)) for url in degrees_url]
    event_rank = download_and_resize_image(event_rank_url, (175, 40))
    event_icon = download_and_resize_image(event_icon_url, (40, 40))

    degrees[1].paste(event_rank, (0, 0), event_rank)
    degrees[1].paste(event_icon, (0, 0), event_icon)
    return degrees

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

    info_box.paste(degrees[0], (100, 150), degrees[0])
    info_box.paste(degrees[1], (325, 150), degrees[1])

    # 乐队卡片（底部对齐）
    card_width, card_height = 100, 100
    start_x = (info_box.width - (card_width + 10) * len(card_images)) // 2
    start_y = 400
    for i, card in enumerate(card_images):
        info_box.paste(card, (start_x + i * (card_width + 10), start_y), card)

    return info_box

def create_cards(cards_url: list[str]) -> list[Image]:
    cards = [download_image(url).resize((100,100)) for url in cards_url]
    for card in cards:
        star_url = "https://bestdori.com/res/icon/star_trained.png"
        star = download_image(star_url).resize((40, 40))
        attr_url = "https://bestdori.com/res/icon/pure.svg"
        attr = download_image(attr_url).resize ((30, 30))
        thumb_frame_url = "https://bestdori.com/res/image/card-5.png"
        thumb_frame = download_image(thumb_frame_url).resize((100, 100))
        card.paste(thumb_frame, (0, 0), thumb_frame)
        card.paste(star, (0, 60), star)
        card.paste(attr, (70, 0), attr)

    return cards

def player_dataImg(user_name: str, rank: int, introduction: str) -> Image:
    """生成玩家信息图片"""
    cards_url = transform_cards([
        "https://bestdori.com/assets/cn/thumb/chara/card00200_rip/bili_res021001_after_training.png",
        "https://bestdori.com/assets/cn/thumb/chara/card00034_rip/res019068_after_training.png",
        "https://bestdori.com/assets/cn/thumb/chara/card00200_rip/bili_res026001_after_training.png",
        "https://bestdori.com/assets/cn/thumb/chara/card00036_rip/res032031_after_training.png",
        "https://bestdori.com/assets/cn/thumb/chara/card00040_rip/res002069_after_training.png"
    ])
    
    degrees_url = [
        "https://bestdori.com/assets/cn/thumb/degree_rip/degree129.png",
        "https://bestdori.com/assets/cn/thumb/degree_rip/degree_event265_point.png"
    ]
    
    event_rank_url = "https://bestdori.com/assets/cn/thumb/degree_rip/event_point_10000.png"
    event_icon_url = "https://bestdori.com/assets/cn/thumb/degree_rip/event_point_icon_10000.png"


    degrees = create_degrees_overlay(degrees_url, event_rank_url, event_icon_url)

    card_images = create_cards(cards_url)
    
    avatar_url = "https://bestdori.com/assets/cn/characters/resourceset/bili_res021001_rip/trim_after_training.png"
    avatar = download_and_resize_image(avatar_url, (800, 800))

    background = create_background()
    background.paste(avatar, (0, -50), avatar)

    info_box = create_info_box(user_name, rank, introduction, degrees, card_images)
    background.paste(info_box, (550, 100), info_box)

    background.save("test.png")
    return background

player_dataImg(user_name, rank, introduction)