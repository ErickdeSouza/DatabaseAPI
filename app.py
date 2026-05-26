from modules  import MainAPI, Token, getSecrets
from fastapi  import FastAPI, WebSocket


app = FastAPI(title="Database API", version="1.5.0")

envs = getSecrets().envs
database = MainAPI(envs)
login = Token(envs)


@app.websocket("/containers")
async def websocket_endpoint(websocket: WebSocket):
    if login.verify(websocket): 
        await websocket.accept()

    while True:
        data = await websocket.receive_json()
        response = database.response(data)
        await websocket.send_json(response)