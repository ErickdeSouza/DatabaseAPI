from fastapi import WebSocket, WebSocketException, status
import jwt


class Token:
    def __init__(self, env: dict|None):
        self.secret = env["SECRET"]
        self.ua = env["USER_AGENT"]

    def verify(self, websocket: WebSocket):
        ua_token = websocket.query_params.get("ua")
        if ua_token != self.ua:
            raise WebSocketException(reason="Wrong User-Agent", code=status.WS_1008_POLICY)
        token = websocket.query_params.get("token")
        try:
            jwt.decode(token, self.secret, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            raise WebSocketException(reason="Expired Token", code=status.WS_1008_POLICY_VIOLATION)
        except jwt.InvalidTokenError:
            raise WebSocketException(reason="Invalid Token", code=status.WS_1008_POLICY_VIOLATION)