import aiohttp
import json
from typing import Any
import diskcache as dc

class AsyncAPIClient:
    def __init__(self, base_url: str, api_file: str, cache_dir: str):
        """
        初始化 API 客户端
        :param base_url: API 服务器地址
        :param api_file: API 配置文件路径
        :param cache_dir: 缓存目录路径
        """
        self.base_url = base_url  # API 服务器地址
        self.api_endpoints = self._load_api_config(api_file)  # 加载 JSON 配置
        self.cache = dc.Cache(cache_dir)  # 初始化缓存

    def _load_api_config(self, file_path: str) -> dict:
        """ 加载 JSON API 配置 """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def fetch(self, endpoint: str, cache: bool = True) -> Any:
        """
        发送异步请求，支持缓存
        :param endpoint: API 端点
        :param params: 请求参数
        :return: API 响应数据
        """
        url = self.base_url + endpoint

        # 检查缓存中是否存在该请求的结果
        if url in self.cache:
            print(f"从缓存中读取数据: {url}")
            return self.cache[url]

        print(f"发送请求: {url}")
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',  # 添加自定义请求头
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.request("GET", url) as response:
                if response.status == 200:
                    data = await response.json()
                    # 将结果保存到缓存
                    if cache:
                        self.cache[url] = data
                        print(f"数据已缓存: {url}")
                    return data
                else:
                    raise Exception(f"请求失败: {response.status}, {await response.text()}")
    
    def delete_cache(self, endpoint: str, params: dict = None):
        """
        删除指定请求的缓存
        :param endpoint: API 端点
        :param params: 请求参数
        """
        url = self.base_url + endpoint
        cache_key = f"{url}:{json.dumps(params, sort_keys=True)}"  # 生成缓存键
        if cache_key in self.cache:
            self.cache.delete(cache_key)
            print(f"缓存已删除: {cache_key}")
        else:
            print(f"缓存不存在: {cache_key}")