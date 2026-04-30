from modules.T001 import FetchData
from modules.T002 import getSecrets
from modules.T003 import Login
from fastapi      import FastAPI, Request, Depends


envs = getSecrets().envs
dbdata = FetchData(envs)
login = Login
login._ENVS = envs

app = FastAPI(title="Database API", version="1.5.0")


@app.get("/ping")
def ping():
    return {"ok": True, "result": "Pong!"}

@app.post("/containers/login")
async def clogin(request: Request):
    return login(request)

@app.get("/containers/get", dependencies=[Depends(login.auth_dependency)])
def ccreate(git: str = None, arg: bool = True):
    return dbdata.get(git, arg)

@app.post("/containers/delete", dependencies=[Depends(login.auth_dependency)])
async def cdelete(request: Request):
    body = await request.json()
    return dbdata.delete(body["git"])

@app.post("/containers/post", dependencies=[Depends(login.auth_dependency)])
async def cpost(request: Request):
    body = await request.json()
    return dbdata.post(body)

@app.get("/containers/code", dependencies=[Depends(login.auth_dependency)])
async def fcode():
    return dbdata.getpy()

@app.post("/containers/code", dependencies=[Depends(login.auth_dependency)])
async def pcode(request: Request):
    body = await request.json()
    return dbdata.postpy(body)

@app.get("/containers/gen", dependencies=[Depends(login.auth_dependency)])
async def fgen():
    return dbdata.getgen()

@app.post("/containers/gen", dependencies=[Depends(login.auth_dependency)])
async def pgen(request: Request):
    body = await request.json()
    return dbdata.postgen(body)

@app.post("/containers/heartbeat", dependencies=[Depends(login.auth_dependency)])
async def update(request: Request):
    body = await request.json()
    return dbdata.heartbeat(body["git"])

@app.get("/containers/commit", dependencies=[Depends(login.auth_dependency)])
def newupdate():
    return dbdata.getValue()