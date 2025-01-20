from p115client import P115Client
from pathlib import Path
import config

class Conn:
	# init the conn
    def __init__(self):
        self.config = config.Config().config_data
        self.cookie = self.config.get('cookie')  # 获取cookie值
        self.client = P115Client(self.cookie)

    # get Client
    def get_client(self):
        return self.client

