from modules.T001 import FetchData
from modules.T002 import getSecrets
from modules.T003 import Token
from fastapi import FastAPI, WebSocket


app = FastAPI(title="Database API", version="1.5.0")

envs = getSecrets().envs
database = FetchData(envs)
login = Token(envs)


@app.websocket("/containers")
async def websocket_endpoint(websocket: WebSocket):
***REMOVED***login.verify(websocket)
***REMOVED***
***REMOVED***while True:
***REMOVED***data = await websocket.receive_json()
***REMOVED***response = database.response(data)
***REMOVED***await websocket.send_json(response)