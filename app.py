from modules.T001 import FetchData
from modules.T002 import getSecrets
from modules.T003 import genToken
from fastapi import FastAPI, Request, Depends

envs = getSecrets().envs
dbdata = FetchData(envs)
auth = genToken(envs)

app = FastAPI(title="Database API", version="1.0.0")

@app.post("/containers/login")
async def clogin(request: Request):
    body = await request.json()
    user =  body.get("user")
    key = body.get("password")
    token = auth.generate_token(key, user)
    if token:
        return {"ok": True, "token": token}

    return {"ok": False, "error": "invalid user/password"}

@app.get("/containers/get", dependencies=[Depends(auth.auth_dependency)])
def ccreate(git: str = None, arg: bool = True):
    return dbdata.get(git, arg)

@app.post("/containers/delete", dependencies=[Depends(auth.auth_dependency)])
async def cdelete(request: Request):
    body = await request.json()
    return dbdata.delete(body["git"])

@app.post("/containers/post", dependencies=[Depends(auth.auth_dependency)])
async def cpost(request: Request):
    body = await request.json()
    return dbdata.post(body)

@app.get("/containers/code", dependencies=[Depends(auth.auth_dependency)])
async def fcode():
    return dbdata.fcode()

@app.post("/containers/code", dependencies=[Depends(auth.auth_dependency)])
async def pcode(request: Request):
    body = await request.json()
    return dbdata.pcode(body)


@app.get("/containers/gen", dependencies=[Depends(auth.auth_dependency)])
async def fgen():
    return dbdata.fgen()

@app.post("/containers/gen", dependencies=[Depends(auth.auth_dependency)])
async def pgen(request: Request):
    body = await request.json()
    return dbdata.pgen(body)


@app.post("/containers/update", dependencies=[Depends(auth.auth_dependency)])
async def update(request: Request):
    body = await request.json()
    return dbdata.upcontainer(body["git"])