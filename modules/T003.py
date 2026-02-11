import hmac, time, hashlib
from fastapi import Header, HTTPException


class genToken:
***REMOVED***def __init__(self, env: dict):
***REMOVED***self.secret_key = env["SECRET_KEY"]
***REMOVED***self.user = env["USER"]

***REMOVED***def generate_token(self, key, user, ttl_seconds: int = 3600):
***REMOVED***if (key, user) != (self.secret_key, self.user):
***REMOVED******REMOVED***return None

***REMOVED***timestamp = int(time.time()) // ttl_seconds
***REMOVED***msg = f"{timestamp}".encode()
***REMOVED***secret = self.secret_key.encode()

***REMOVED***token = hmac.new(secret, msg, hashlib.sha256).hexdigest()
***REMOVED***return token

***REMOVED***def validate_token(self, token: str, ttl_seconds: int = 3600):
***REMOVED***timestamp = int(time.time()) // ttl_seconds
***REMOVED***secret = self.secret_key.encode()

***REMOVED***for t in (timestamp, timestamp - 1):
***REMOVED******REMOVED***msg = f"{t}".encode()
***REMOVED******REMOVED***expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()
***REMOVED******REMOVED***if hmac.compare_digest(expected, token):
***REMOVED******REMOVED***return True

***REMOVED***return False

***REMOVED***def auth_dependency(self, authorization: str = Header(None)):
***REMOVED***if not authorization or not authorization.startswith("Bearer "):
***REMOVED******REMOVED***raise HTTPException(status_code=401, detail="Token ausente")

***REMOVED***token = authorization.split(" ")[1]

***REMOVED***if not self.validate_token(token):
***REMOVED******REMOVED***raise HTTPException(status_code=403, detail="Token inválido")