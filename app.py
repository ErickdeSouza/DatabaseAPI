from modules  import MainAPI, Token, getSecrets
from fastapi  import FastAPI, WebSocket


app = FastAPI(title="Database API", version="1.5.0")

envs = getSecrets().envs
database = MainAPI(envs)
login = Token(envs)


@app.websocket("/containers")
async def websocket_endpoint(websocket: WebSocket):
***REMOVED***if login.verify(websocket): 
***REMOVED***await websocket.accept()
***REMOVED***
***REMOVED***while True:
***REMOVED***data = await websocket.receive_json()
***REMOVED***response = database.response(data)
***REMOVED***await websocket.send_json(response)