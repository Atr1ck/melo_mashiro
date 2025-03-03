import os
import aiohttp
from io import BytesIO
from PIL import Image
import cairosvg
import asyncio
import lxml.etree as etree

async def download_image(url):
    """异步下载图片，支持 SVG 转换"""
    print(url)
    if url.endswith(".svg"):
        svg_filename = src/cache
        
        if os.path.exists(svg_filename):
            # 从本地读取 SVG 文件
            with open(svg_filename, 'rb') as svg_file:
                svg_content = svg_file.read()

            # 使用 cairosvg 将 SVG 转换为 PNG
            png_data = await asyncio.to_thread(cairosvg.svg2png, bytestring=svg_content)
            return Image.open(BytesIO(png_data)).convert("RGBA")
        else:
            raise Exception(f"SVG 文件 {svg_filename} 未找到")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                return Image.open(BytesIO(content)).convert("RGBA")
            else:
                raise Exception(f"无法下载图片: {url}, 状态码: {response.status}")
import asyncio

async def main():
    url = "https://bestdori.com/res/icon/pure.svg"  # 替换为你的 SVG 图片 URL
    image = await download_image(url)
    

asyncio.run(main())