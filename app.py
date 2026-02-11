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
***REMOVED***body = await request.json()
***REMOVED***user =  body.get("user")
***REMOVED***key = body.get("password")
***REMOVED***token = auth.generate_token(key, user)
***REMOVED***if token:
***REMOVED***return {"ok": True, "token": token}

***REMOVED***return {"ok": False, "error": "invalid user/password"}

@app.get("/containers/get", dependencies=[Depends(auth.auth_dependency)])
def ccreate(git: str = None, arg: bool = True):
***REMOVED***return dbdata.get(git, arg)

@app.post("/containers/delete", dependencies=[Depends(auth.auth_dependency)])
async def cdelete(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.delete(body["git"])

@app.post("/containers/post", dependencies=[Depends(auth.auth_dependency)])
async def cpost(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.post(body)

@app.get("/containers/code", dependencies=[Depends(auth.auth_dependency)])
async def fcode():
***REMOVED***return dbdata.fcode()

@app.post("/containers/code", dependencies=[Depends(auth.auth_dependency)])
async def pcode(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.pcode(body)


@app.get("/containers/gen", dependencies=[Depends(auth.auth_dependency)])
async def fgen():
***REMOVED***return dbdata.fgen()

@app.post("/containers/gen", dependencies=[Depends(auth.auth_dependency)])
async def pgen(request: Request):
***REMOVED***body = await request.json()
***REMOVED***return dbdata.pgen(body)