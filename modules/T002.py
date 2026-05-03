from dotenv  import dotenv_values, load_dotenv
from pathlib import Path
import os

class getSecrets:
***REMOVED***def __init__(self, arg=False):
***REMOVED***load_dotenv()
***REMOVED***self.envs = self.get(arg)

***REMOVED***def get(self, arg):
***REMOVED***if arg:
***REMOVED******REMOVED***ENV_PATH = Path(__file__).resolve() / ".env"
***REMOVED******REMOVED***return dotenv_values(dotenv_path=ENV_PATH)

***REMOVED***key = ["APPY_GIT_TOKEN", "APPY_DB_URL", "SECRET_KEY", "USER", "SECRET", "USER_AGENT"]
***REMOVED***return {
***REMOVED******REMOVED***item: os.getenv(item)
***REMOVED******REMOVED***for item in key
***REMOVED******REMOVED***}