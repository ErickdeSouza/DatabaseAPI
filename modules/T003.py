import hmac, time, hashlib
from fastapi import Header, HTTPException


class genToken:
    def __init__(self, env: dict):
        self.secret_key = env["SECRET_KEY"]
        self.user = env["USER"]

    def generate_token(self, key, user, ttl_seconds: int = 3600):
        if (key, user) != (self.secret_key, self.user):
            return None

        timestamp = int(time.time()) // ttl_seconds
        msg = f"{timestamp}".encode()
        secret = self.secret_key.encode()

        token = hmac.new(secret, msg, hashlib.sha256).hexdigest()
        return token

    def validate_token(self, token: str, ttl_seconds: int = 3600):
        timestamp = int(time.time()) // ttl_seconds
        secret = self.secret_key.encode()

        for t in (timestamp, timestamp - 1):
            msg = f"{t}".encode()
            expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected, token):
                return True

        return False

    def auth_dependency(self, authorization: str = Header(None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token ausente")

        token = authorization.split(" ")[1]

        if not self.validate_token(token):
            raise HTTPException(status_code=403, detail="Token inválido")