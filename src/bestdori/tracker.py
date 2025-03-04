import base64
import io
from bestdori.API.api import AsyncAPIClient
from configparser import ConfigParser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import datetime

config = ConfigParser()

config.read("src/config.conf")

API_PATH = config.get("Bestdori", "API_PATH")
CACHE_PATH = config.get("Cache", "CACHE_PATH")
FONT_PATH = config.get("Fonts", "FONTS_PATH")

my_font = fm.FontProperties(fname=FONT_PATH)

plt.rcParams["font.family"] = my_font.get_name()

class Tracker:
    def __init__(self, event_info, tier):
        self.scoreWithTime = event_info["cutoffs"]
        self.tier = tier

    async def drawImage(self):
        # 提取时间和值
        timestamps = [entry["time"] for entry in self.scoreWithTime]
        values = [entry["ep"] for entry in self.scoreWithTime]

        # 将时间戳转换为北京时间（UTC+8）
        beijing_times = [datetime.datetime.fromtimestamp(ts / 1000, tz=datetime.timezone(datetime.timedelta(hours=8))) for ts in timestamps]

        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(beijing_times, values, linestyle="-", color="b")

        # 设置标题和标签
        ax.set_title(f"邦邦本期活动T{self.tier}活动P")
        ax.set_xlabel("时间")
        ax.set_ylabel("活动P")

        # 格式化横坐标：每天一个刻度
        ax.xaxis.set_major_locator(mdates.DayLocator())  # 每天一个刻度
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))  # 只显示日期
        fig.autofmt_xdate()  # 自动旋转日期标签

        # 调整布局
        fig.tight_layout()

        # **将图片保存到 BytesIO 对象**
        buf = io.BytesIO()
        fig.savefig(buf, format="png")  # 以 PNG 格式保存到内存
        plt.close(fig)  # 关闭 Matplotlib 图像，释放内存
        buf.seek(0)  # 重置缓冲区指针

        # **转换为 Base64**
        img_base64 = f"base64://{base64.b64encode(buf.getvalue()).decode("utf-8")}"
        return img_base64

async def get_now_event(tier):
    client = AsyncAPIClient("https://bestdori.com", API_PATH, CACHE_PATH)
    events_all = await client.fetch(client.api_endpoints["events"]["all"].format(index=1), cache=False)
    now_event = 0
    for index, item in enumerate(events_all.values()):
        if item["eventName"][3] == None:
            now_event = index
            break
    
    event_info = await client.fetch(client.api_endpoints["tracker"]["eventtracker"].format(server=3, eventId=now_event, tier=tier), cache=False)
    tracker = Tracker(event_info, tier)
    image_base64 = await tracker.drawImage()
    return image_base64
