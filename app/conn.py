from p115client import P115Client
from pathlib import Path
import config

class Conn:
	# init the conn
    def __init__(self):
        self.config = config.Config().get_config()
        self.client = P115Client(Path("config/cookie.txt"))

    # get Client
    def get_client(self):
        return self.client

