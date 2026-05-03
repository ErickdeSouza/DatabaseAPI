from datetime***REMOVED***import datetime
from zoneinfo***REMOVED***import ZoneInfo
from psycopg2.extras import Json, DictConnection
import time, psycopg2, random, base64, threading, requests


CONNECTIONS = 0 


class GitHub:
***REMOVED***_OWNER = "ErickdeSouza"
***REMOVED***_REPO = "Private-container"
***REMOVED***
***REMOVED***def __init__(self, env, conn: DictConnection|None = None):
***REMOVED***self.env = env
***REMOVED***self.conn = conn
***REMOVED***self.id = "1a1e5709-8e45-4db5-a3c2-3edb8c844ae4"
***REMOVED***self.last_commit = self.lastCommit()
***REMOVED***self.trigger = False
***REMOVED***
***REMOVED***"""Abaixo a parte do Github API. Nova implementacao a essa API devido a necessidade de updates dos containers."""
***REMOVED***def getTable(self):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute('SELECT node_id FROM commits WHERE id = %s', (self.id,))
***REMOVED******REMOVED***r = cur.fetchone()
***REMOVED******REMOVED***
***REMOVED******REMOVED***return {"node_id": r[0]} 
***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return None
***REMOVED***
***REMOVED***def updateTable(self, node_id):
***REMOVED***cur = self.conn.cursor()
***REMOVED***cur.execute("""
***REMOVED******REMOVED***UPDATE commits
***REMOVED******REMOVED***SET node_id = %s
***REMOVED******REMOVED***WHERE id = %s
***REMOVED******REMOVED***""", (node_id, self.id)
***REMOVED***
***REMOVED***self.conn.commit()
***REMOVED******REMOVED***
***REMOVED***def lastCommit(self):
***REMOVED***headers = {
***REMOVED******REMOVED***"Accept": "application/vnd.github+json",
***REMOVED******REMOVED***"Authorization": f"Bearer {self.env["APPY_GIT_TOKEN"]}",
***REMOVED******REMOVED***"X-GitHub-Api-Version": "2026-03-10"
***REMOVED***}
***REMOVED***resp = requests.get(f"https://api.github.com/repos/{GitHub._OWNER}/{GitHub._REPO}/commits", headers=headers)
***REMOVED***
***REMOVED***if resp.status_code == 200:
***REMOVED******REMOVED***data = resp.json()[0]["node_id"]
***REMOVED******REMOVED***return data

***REMOVED***return None
***REMOVED******REMOVED***
***REMOVED***def getValue(self):
***REMOVED***return {"ok": True, "result": self.trigger}
***REMOVED***
***REMOVED***def verifyC(self):
***REMOVED***while True:
***REMOVED******REMOVED***if not self.last_commit:
***REMOVED******REMOVED***self.last_commit = self.lastCommit()
***REMOVED******REMOVED***continue
***REMOVED******REMOVED***
***REMOVED******REMOVED***table = self.getTable()
***REMOVED******REMOVED***if table:
***REMOVED******REMOVED***if self.last_commit != table["node_id"]:
***REMOVED******REMOVED******REMOVED***self.trigger = True
***REMOVED******REMOVED******REMOVED***self.updateTable(table["node_id"])
***REMOVED******REMOVED***else:
***REMOVED******REMOVED******REMOVED***self.trigger = False***REMOVED***
***REMOVED******REMOVED***
***REMOVED******REMOVED***time.sleep(7200)


class FetchData(GitHub):
***REMOVED***def __init__(self, env, test: bool|None = None):
***REMOVED***self.conn = psycopg2.connect(env["APPY_DB_URL"], sslmode="require")
***REMOVED***super().__init__(env, self.conn)
***REMOVED***
***REMOVED***#payload requerido na resposta recebida pelo user
***REMOVED***self.required = ("tw", "dt")
***REMOVED***self.twcodes = [
***REMOVED***i for i in range(1, 7)],
***REMOVED******REMOVED***(1, [self.getgen, self.postgen]),
***REMOVED******REMOVED***(2, [self.getpy, self.postpy]),
***REMOVED******REMOVED***(3, self.heartbeat),
***REMOVED******REMOVED***(4, self.get),
***REMOVED******REMOVED***(5, self.post),
***REMOVED******REMOVED***(6, self.delete)***REMOVED***  
***REMOVED***]
***REMOVED***
***REMOVED***if not test:
***REMOVED******REMOVED***threading.Thread(target=self.verifVm).start()
***REMOVED******REMOVED***threading.Thread(target=self.verifyC).start()
***REMOVED***
***REMOVED***def manager(self, data: dict):
***REMOVED***resp = None
***REMOVED***
***REMOVED***#verify do payload
***REMOVED***for item in data.keys():
***REMOVED******REMOVED***if not item in self.required:
***REMOVED******REMOVED***return {"tw": 0, "dt": {"error": f'"{item}" está faltando no seu body.'}}
***REMOVED******REMOVED***
***REMOVED***if data["tw"] not in self.twcodes[0]:
***REMOVED******REMOVED***return {"tw": 0, "dt": {"error": 'O código do seu "tw" não existe ou é invalido.'}}
***REMOVED***
***REMOVED***for code, func in self.twcodes[1:]:
***REMOVED******REMOVED***if code >= 3 and code == data["tw"]:
***REMOVED******REMOVED***resp = func(data["dt"])
***REMOVED******REMOVED***
***REMOVED******REMOVED***elif code == data["tw"]:
***REMOVED******REMOVED***method = data["dt"]["method"]
***REMOVED***
***REMOVED******REMOVED***if method == "get":
***REMOVED******REMOVED******REMOVED***resp = func[0](data["dt"])
***REMOVED******REMOVED***elif method == "post":
***REMOVED******REMOVED******REMOVED***resp = func[1](data["dt"])
***REMOVED***
***REMOVED***return resp
***REMOVED******REMOVED***
***REMOVED***def response(self, data):
***REMOVED***resp = self.manager(data)
***REMOVED***if not resp:
***REMOVED******REMOVED***return {"tw": 0, "dt": {"error": 'Alguma coisa deu errado...'}}
***REMOVED***
***REMOVED***return {"tw": 7, "dt": resp}
***REMOVED***
***REMOVED***
***REMOVED***"""Abaixo encontra a parte de Database. Depois de resolvido problemas de timestamp, nada fora do normal aqui."""
***REMOVED***def post(self, d):# twcode: 5
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***INSERT INTO accounts (git_url, ssh_key, priv_key, email, password, heartbeat)
***REMOVED******REMOVED***VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING git_url
***REMOVED******REMOVED***""", (d["git_url"], d["ssh_key"], d["priv_key"], d["email"], d["password"]))
***REMOVED******REMOVED***account_id = cur.fetchone()[0]
***REMOVED******REMOVED***self.conn.commit()

***REMOVED******REMOVED***return {"ok": True, "id": account_id}
***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}

***REMOVED***def get(self, git_id=None, arg=False):# twcode: 4
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***if git_id:
***REMOVED******REMOVED***cur.execute(
***REMOVED******REMOVED******REMOVED***"SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat "
***REMOVED******REMOVED******REMOVED***"FROM accounts WHERE git_url = %s",
***REMOVED******REMOVED******REMOVED***(git_id,)
***REMOVED******REMOVED***
***REMOVED******REMOVED***elif not git_id:
***REMOVED******REMOVED***cur.execute("SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat FROM accounts")
***REMOVED******REMOVED***
***REMOVED******REMOVED***rows = cur.fetchall()
***REMOVED******REMOVED***return {"ok": True, "result": [{
***REMOVED******REMOVED******REMOVED***"id": str(r[0]),
***REMOVED******REMOVED******REMOVED***"git_url": r[1],
***REMOVED******REMOVED******REMOVED***"email": r[2],
***REMOVED******REMOVED******REMOVED***"ssh_key": r[3] if arg else None,
***REMOVED******REMOVED******REMOVED***"priv_key": r[4] if arg else None,
***REMOVED******REMOVED******REMOVED***"password": r[5],
***REMOVED******REMOVED******REMOVED***"time": r[6],
***REMOVED******REMOVED******REMOVED***"heartbeat": r[7]
***REMOVED******REMOVED***} for r in rows]
***REMOVED******REMOVED***}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}

***REMOVED***def delete(self, git):# twcode: 6
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("DELETE FROM accounts WHERE git_url= %s RETURNING id", (git,))
***REMOVED******REMOVED***deleted = cur.fetchone()
***REMOVED******REMOVED***self.conn.commit()
***REMOVED******REMOVED***if not deleted:
***REMOVED******REMOVED***return {"ok": False, "func_error": "Conta não encontrada..."}

***REMOVED******REMOVED***return {"ok": True, "id": str(deleted[0])}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
***REMOVED***
***REMOVED***
***REMOVED***def getpy(self):# twcode: 2
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***SELECT code 
***REMOVED******REMOVED***FROM container WHERE id = %s""", ("2b66698d-4995-410a-9a7d-3a462b25e323",)
***REMOVED******REMOVED***
***REMOVED******REMOVED***
***REMOVED******REMOVED***r = cur.fetchone()
***REMOVED******REMOVED***return {"ok": True, "result": r[0]}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
***REMOVED******REMOVED***
***REMOVED***def postpy(# twcode: 2
***REMOVED***self,
***REMOVED***response: dict, #Keys necessarias: "edit", "code", "amount", "package" or "change"
***REMOVED***):
***REMOVED***try:
***REMOVED******REMOVED***if not self.fcode()["ok"] and response["edit"]:
***REMOVED******REMOVED***return {"ok": False, "func_error": "Nenhuma dado retornado em code...."}
***REMOVED******REMOVED***
***REMOVED******REMOVED***if not response["edit"]:
***REMOVED******REMOVED***vms = []
***REMOVED******REMOVED***data = []
***REMOVED******REMOVED***gg = self.get()["result"]
***REMOVED******REMOVED***cur = self.conn.cursor()

***REMOVED******REMOVED***data_str = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")
***REMOVED******REMOVED***amount = int(response["amount"])

***REMOVED******REMOVED***if len(gg) < 0 or len(gg) < amount:
***REMOVED******REMOVED******REMOVED***return {
***REMOVED******REMOVED******REMOVED***"ok": False,
***REMOVED******REMOVED******REMOVED***"func_error": f"AmountError: Poucos containers existentes..."
***REMOVED******REMOVED******REMOVED***}

***REMOVED******REMOVED***for vm in gg:
***REMOVED******REMOVED******REMOVED***if len(vms) == amount:
***REMOVED******REMOVED******REMOVED***break
***REMOVED******REMOVED******REMOVED***vms.append(vm["git_url"])

***REMOVED******REMOVED***data.append({
***REMOVED******REMOVED******REMOVED***"code": base64.b64encode(response["code"].encode("utf-8")).decode("utf-8"),
***REMOVED******REMOVED******REMOVED***"package": base64.b64encode(response["package"].encode("utf-8")).decode("utf-8") if response["package"] else None
***REMOVED******REMOVED***})

***REMOVED******REMOVED***samplevm = random.sample(vms, k=amount)
***REMOVED******REMOVED***for i in samplevm:
***REMOVED******REMOVED******REMOVED***data.append({
***REMOVED******REMOVED******REMOVED***"id": "vm_" + i.split(".com:")[1].split(".git")[0],
***REMOVED******REMOVED******REMOVED***"git": i,
***REMOVED******REMOVED******REMOVED***"run": False,
***REMOVED******REMOVED******REMOVED***"data": {
***REMOVED******REMOVED******REMOVED******REMOVED***"error": False,
***REMOVED******REMOVED******REMOVED******REMOVED***"result": "Aguardando resposta....",
***REMOVED******REMOVED******REMOVED******REMOVED***"time": data_str
***REMOVED******REMOVED******REMOVED***}
***REMOVED******REMOVED******REMOVED***})


***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED******REMOVED***UPDATE container
***REMOVED******REMOVED******REMOVED***SET code = %s
***REMOVED******REMOVED******REMOVED***WHERE id = %s
***REMOVED******REMOVED******REMOVED***""", (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
***REMOVED******REMOVED***
***REMOVED******REMOVED***self.conn.commit()

***REMOVED******REMOVED***return {
***REMOVED******REMOVED******REMOVED***"ok": True,
***REMOVED******REMOVED******REMOVED***"result": f"Sucess: Seu codigo estará rodando em {amount} containers!"
***REMOVED******REMOVED***}


***REMOVED******REMOVED***elif response["edit"]:
***REMOVED******REMOVED***data = self.fcode()["result"]["data"]
***REMOVED******REMOVED***resp = response["change"]

***REMOVED******REMOVED***for vms in data[1:]:
***REMOVED******REMOVED******REMOVED***if resp["id"] == vms["id"]:
***REMOVED******REMOVED******REMOVED***vms.update({"run": resp["run"], "data": resp["data"]})

***REMOVED******REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED******REMOVED******REMOVED***UPDATE container
***REMOVED******REMOVED******REMOVED******REMOVED***SET code = %s
***REMOVED******REMOVED******REMOVED******REMOVED***WHERE id = %s
***REMOVED******REMOVED******REMOVED******REMOVED***""", (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED******REMOVED***self.conn.commit()

***REMOVED******REMOVED******REMOVED***return {
***REMOVED******REMOVED******REMOVED******REMOVED***"ok": True,
***REMOVED******REMOVED******REMOVED******REMOVED***"result": f"Editado com sucesso! vmid: {resp["id"]}"
***REMOVED******REMOVED******REMOVED***}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
***REMOVED******REMOVED***
***REMOVED******REMOVED***
***REMOVED***def getgen(self): # twcode: 1
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***SELECT gen 
***REMOVED******REMOVED***FROM container WHERE id = %s""", ("2b66698d-4995-410a-9a7d-3a462b25e323",)
***REMOVED******REMOVED***
***REMOVED******REMOVED***r = cur.fetchone()
***REMOVED******REMOVED***return {"ok": True, "result": r[0]}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}

***REMOVED***def postgen(# twcode: 1
***REMOVED***self,
***REMOVED***response: dict, #Keys necessarias: "vms", "create" or "del" or "verif"
***REMOVED***):
***REMOVED***try:
***REMOVED******REMOVED***if not self.fgen()["ok"] and not response["create"]:
***REMOVED******REMOVED***return {"ok": False, "func_error": "Nenhuma dado retornado em gen...."}
***REMOVED******REMOVED***
***REMOVED******REMOVED***if response["create"]:
***REMOVED******REMOVED***data = {
***REMOVED******REMOVED******REMOVED***"create": True,
***REMOVED******REMOVED******REMOVED***"info": {
***REMOVED******REMOVED******REMOVED***"request": int(response["vms"]),
***REMOVED******REMOVED******REMOVED***"created": 0,
***REMOVED******REMOVED******REMOVED***"started": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" ")
***REMOVED******REMOVED******REMOVED***},
***REMOVED******REMOVED******REMOVED***"finished": None
***REMOVED******REMOVED***}
***REMOVED******REMOVED***self.upgen(data)
***REMOVED******REMOVED***return {"ok": True, "All": False, "result": f"Solicitada a criação de {response["vms"]} containers!"}
***REMOVED******REMOVED***
***REMOVED******REMOVED***elif response["del"]:
***REMOVED******REMOVED***data = self.fgen()["result"]["data"]
***REMOVED******REMOVED***if data["info"]["request"] == data["info"]["created"]:
***REMOVED******REMOVED******REMOVED***lol = self.tempo(data["info"]["started"], datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" "))
***REMOVED******REMOVED******REMOVED***data.update({"create": False, "finished": lol})
***REMOVED******REMOVED******REMOVED***self.upgen(data)
***REMOVED******REMOVED******REMOVED***return {"ok": True, "All": True, "result": f"Todos containers solicitados já criados!"}
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED***data["info"]["created"] += 1
***REMOVED******REMOVED***self.upgen(data)
***REMOVED******REMOVED***return {"ok": True, "All": False, "result": f"+1 container criado!"}
***REMOVED******REMOVED***
***REMOVED******REMOVED***elif response["verif"]:
***REMOVED******REMOVED***data = self.fgen()["result"]["data"]
***REMOVED******REMOVED***if data["info"]["request"] == data["info"]["created"]:
***REMOVED******REMOVED******REMOVED***return {"ok": True, "result": f"Todos containers solicitados já criados!"}
***REMOVED******REMOVED***
***REMOVED******REMOVED***return {"ok": True, "result": f"{data["info"]["created"]} containers criados no momento."}
***REMOVED******REMOVED***
***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
***REMOVED***
***REMOVED***def upgen(self, data):
***REMOVED***cur = self.conn.cursor()
***REMOVED***cur.execute("""
***REMOVED******REMOVED***UPDATE container
***REMOVED******REMOVED***SET gen = %s
***REMOVED******REMOVED***WHERE id = %s
***REMOVED******REMOVED***""", (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
***REMOVED***
***REMOVED***self.conn.commit()
***REMOVED***
***REMOVED***
***REMOVED***def heartbeat(self, git): # twcode: 3
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***UPDATE accounts
***REMOVED******REMOVED***SET heartbeat = NOW()
***REMOVED******REMOVED***WHERE git_url = %s""", (git,)
***REMOVED******REMOVED***
***REMOVED******REMOVED***self.conn.commit()
***REMOVED******REMOVED***
***REMOVED******REMOVED***return {"ok": True}
***REMOVED***except Exception as e:
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
***REMOVED***
***REMOVED***
***REMOVED***def verifVm(self):
***REMOVED***while True:
***REMOVED******REMOVED***try:
***REMOVED******REMOVED***data = self.get()["result"]
***REMOVED******REMOVED***for i in data:
***REMOVED******REMOVED******REMOVED***timestamp = datetime.fromisoformat(str(i["heartbeat"]))
***REMOVED******REMOVED******REMOVED***if timestamp.tzinfo is not None:
***REMOVED******REMOVED******REMOVED***timestamp = timestamp.replace(tzinfo=None)

***REMOVED******REMOVED******REMOVED***agora = datetime.now()
***REMOVED******REMOVED******REMOVED***diff = (agora - timestamp).total_seconds()

***REMOVED******REMOVED******REMOVED***if diff >= 1200:
***REMOVED******REMOVED******REMOVED***print("deletado")
***REMOVED******REMOVED******REMOVED***self.delete(i["git_url"])
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED***except Exception as e:
***REMOVED******REMOVED***print("Erro:", e)

***REMOVED******REMOVED***time.sleep(7)***REMOVED*** 
***REMOVED******REMOVED***
***REMOVED***@staticmethod
***REMOVED***def tempo(ts_inicio: str, ts_fim: str):
***REMOVED***inicio = datetime.fromisoformat(ts_inicio)
***REMOVED***fim = datetime.fromisoformat(ts_fim)

***REMOVED***total_segundos = int((fim - inicio).total_seconds())

***REMOVED***horas = total_segundos // 3600
***REMOVED***minutos = (total_segundos % 3600) // 60

***REMOVED***if horas > 0:
***REMOVED******REMOVED***return f"{horas} horas e {minutos} minutos"
***REMOVED***else:
***REMOVED******REMOVED***return f"{minutos} minutos"