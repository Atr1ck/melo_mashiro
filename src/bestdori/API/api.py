import aiohttp
import json
from typing import Any

class AsyncAPIClient:
    def __init__(self, base_url: str, api_file: str):
        self.base_url = base_url  # API 服务器地址
        self.api_endpoints = self._load_api_config(api_file)  # 加载 JSON 配置

    def _load_api_config(self, file_path: str) -> dict:
        """ 加载 JSON API 配置 """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def fetch(self, endpoints, params=None) -> Any:
        """ 发送异步请求，支持 GET/POST """
        url = self.base_url + endpoints

        async with aiohttp.ClientSession() as session:
            async with session.request("GET", url, params=params) as response:
                return await response.json()

