from bestdori.API.api import AsyncAPIClient
from configparser import ConfigParser

config = ConfigParser()

config.read("src/config.conf")

API_PATH = config.get("Bestdori", "API_PATH")

class Degree():
    def __init__(self, degree_info, id):
        self.id = id
        self.baseImageName = degree_info[str(id)]["baseImageName"][3]
        self.iconImageName = degree_info[str(id)]["iconImageName"][3]
        self.degreeName = degree_info[str(id)]["degreeName"][3]
        self.degreeType = degree_info[str(id)]["degreeType"][3]
        self.rank = degree_info[str(id)]["rank"][3]

    def get_event(self):
        event_url = f"https://bestdori.com/assets/cn/thumb/degree_rip/{self.baseImageName}.png"
        return event_url

    def get_rank(self):
        rank_url = f"https://bestdori.com/assets/cn/thumb/degree_rip/{self.degreeType}_{self.rank}.png"
        return rank_url
    
    def get_icon(self):
        icon_url = f"https://bestdori.com/assets/cn/thumb/degree_rip/{self.iconImageName}_{self.rank}.png"
        return icon_url

async def get_degree(id):
    client = AsyncAPIClient("https://bestdori.com", API_PATH)
    degree_info = await client.fetch(client.api_endpoints["all"]["degrees"].format(index=3))
    degree = Degree(degree_info, id)
    return degree