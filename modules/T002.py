from dotenv import dotenv_values, load_dotenv
from pathlib import Path
import os

class getSecrets:
***REMOVED***def __init__(self, arg=False):
***REMOVED***load_dotenv()
***REMOVED***self.envs = self.get(arg)

***REMOVED***def get(self, arg):
***REMOVED***key = ["APPY_DB_URL", "SECRET_KEY", "USER"]
***REMOVED***if arg:
***REMOVED******REMOVED***ENV_PATH = Path(__file__).resolve() / ".env"
***REMOVED******REMOVED***return dotenv_values(dotenv_path=ENV_PATH)

***REMOVED***return {
***REMOVED******REMOVED***key[0]: os.getenv(key[0]),
***REMOVED******REMOVED***key[1]: os.getenv(key[1]),
***REMOVED******REMOVED***key[2]: os.getenv(key[2])
***REMOVED******REMOVED***}