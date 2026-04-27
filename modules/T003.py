from fastapi import Header, HTTPException, Request
import hmac, time, hashlib, asyncio


class genToken:
***REMOVED***def __init__(self, env: dict|None):
***REMOVED***if not env:
***REMOVED******REMOVED***self.secret_key = env["SECRET_KEY"]
***REMOVED******REMOVED***self.user = env["USER"]

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
***REMOVED***

class Login(genToken):
***REMOVED***_ENVS = None
***REMOVED***
***REMOVED***def __int__(self, request: Request|None = None):
***REMOVED***super().__init__(Login._ENVS)
***REMOVED***if request:
***REMOVED******REMOVED***return self.signup(request)
***REMOVED***
***REMOVED***async def _signup(self, request: Request):
***REMOVED***body = await request.json()
***REMOVED***user =  str(body.get("user"))
***REMOVED***key = str(body.get("password"))
***REMOVED***token = self.generate_token(key, user)
***REMOVED***if token:
***REMOVED******REMOVED***return {"ok": True, "token": token}

***REMOVED***return {"ok": False, "error": "invalid user/password"}
***REMOVED***
***REMOVED***def signup(self, req):
***REMOVED***return asyncio.run(self._signup(req))