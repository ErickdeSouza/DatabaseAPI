from dotenv import dotenv_values, load_dotenv
from pathlib import Path
import os

class getSecrets:
    def __init__(self, arg=False):
        load_dotenv()
        self.envs = self.get(arg)

    def get(self, arg):
        key = ["APPY_DB_URL", "SECRET_KEY", "USER"]
        if arg:
            ENV_PATH = Path(__file__).resolve() / ".env"
            return dotenv_values(dotenv_path=ENV_PATH)

        return {
                key[0]: os.getenv(key[0]),
                key[1]: os.getenv(key[1]),
                key[2]: os.getenv(key[2])
            }