from dotenv  import dotenv_values, load_dotenv
from pathlib import Path
import os

class getSecrets:
    def __init__(self, arg=False):
        load_dotenv()
        self.envs = self.get(arg)

    def get(self, arg):
        if arg:
            ENV_PATH = Path(__file__).resolve() / ".env"
            return dotenv_values(dotenv_path=ENV_PATH)

        key = ["APPY_GIT_TOKEN", "APPY_DB_URL", "SECRET_KEY", "USER", "SECRET", "USER_AGENT"]
        return {
            item: os.getenv(item)
            for item in key
        }