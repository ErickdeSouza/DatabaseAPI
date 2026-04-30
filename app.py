from modules.T001 import FetchData
from modules.T002 import getSecrets
from modules.T003 import Login
from fastapi***REMOVED***  import FastAPI, Request, Depends


envs = getSecrets().envs
dbdata = FetchData(envs)
login = Login
login._ENVS = envs

app = FastAPI(title="Database API", version="1.5.0")


@app.get("/ping")
def ping():
***REMOVED***return {"ok": True, "result": "Pong!"}

@app.post("/containers/login")
async def clogin(request: Request):
***REMOVED***return login(request)

@app.get("/containers/get", dependencies=[Depends(login.auth_dependency)])
def ccreate(git: str = None, arg: bool = True):
***REMOVED***return dbdata.get(git, arg)

@app.post("/containers/delete", dependencies=[Depends(login.auth_dependency)])
async def cdelete(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.delete(body["git"])

@app.post("/containers/post", dependencies=[Depends(login.auth_dependency)])
async def cpost(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.post(body)

@app.get("/containers/code", dependencies=[Depends(login.auth_dependency)])
async def fcode():
***REMOVED***return dbdata.getpy()

@app.post("/containers/code", dependencies=[Depends(login.auth_dependency)])
async def pcode(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.postpy(body)

@app.get("/containers/gen", dependencies=[Depends(login.auth_dependency)])
async def fgen():
***REMOVED***return dbdata.getgen()

@app.post("/containers/gen", dependencies=[Depends(login.auth_dependency)])
async def pgen(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.postgen(body)

@app.post("/containers/heartbeat", dependencies=[Depends(login.auth_dependency)])
async def update(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.heartbeat(body["git"])

@app.get("/containers/commit", dependencies=[Depends(login.auth_dependency)])
def newupdate():
***REMOVED***return dbdata.getValue()