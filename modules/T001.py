from datetime***REMOVED***import datetime
from zoneinfo***REMOVED***import ZoneInfo
from psycopg2.extras import Json, DictConnection
from modules.T004***REMOVED***import ScalingoDeployer, FetchRepo
from modules.T005***REMOVED***import Separate
import time, psycopg2, random, base64, threading, requests




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
***REMOVED***

class MainAPI(GitHub):
***REMOVED***def __init__(self, env, test: bool|None = None):
***REMOVED***self.conn = psycopg2.connect(env["APPY_DB_URL"], sslmode="require")
***REMOVED***super().__init__(env, self.conn)
***REMOVED***self.commit = ScalingoDeployer()
***REMOVED***#payload requerido na resposta recebida pelo user
***REMOVED***self.required = ("tw", "dt")
***REMOVED***self.twcodes = [
***REMOVED***i for i in range(1, 7)],
***REMOVED******REMOVED***(1, [self.getgen, self.postgen]),
***REMOVED******REMOVED***(2, [self.getpy, self.postpy]),
***REMOVED******REMOVED***(3, self.heartbeat),
***REMOVED******REMOVED***(4, self.get),
***REMOVED******REMOVED***(5, self.post),
***REMOVED******REMOVED***(6, self.delete) 
***REMOVED***]
***REMOVED***if not test:
***REMOVED******REMOVED***threading.Thread(target=self.verifVm).start()
***REMOVED******REMOVED***threading.Thread(target=self.verifyC).start()
***REMOVED***
***REMOVED***def manager(self, data: dict):
***REMOVED***#verify do payload
***REMOVED***for item in data.keys():
***REMOVED******REMOVED***if not item in self.required:
***REMOVED******REMOVED***return {"tw": 67, "dt": {"error": f'"{item}" está faltando no seu body.'}}
***REMOVED******REMOVED***
***REMOVED***if data["tw"] not in self.twcodes[0]:
***REMOVED******REMOVED***return {"tw": 67, "dt": {"error": 'O código do seu "tw" não existe ou é invalido.'}}
***REMOVED***
***REMOVED***for code, func in self.twcodes[1:]:
***REMOVED******REMOVED***if type(func) != list and code == data["tw"]:
***REMOVED******REMOVED***return func(data["dt"])
***REMOVED******REMOVED***
***REMOVED******REMOVED***method = data["dt"]["method"]
***REMOVED******REMOVED***if method == "get":
***REMOVED******REMOVED***return func[0]()
***REMOVED******REMOVED***elif method == "post":
***REMOVED******REMOVED***return func[1](data["dt"])
***REMOVED******REMOVED***
***REMOVED***def response(self, data):
***REMOVED***resp = self.manager(data)
***REMOVED***if not resp:
***REMOVED******REMOVED***return {"tw": 67, "dt": {"error": 'Alguma coisa deu errado...'}}
***REMOVED***return {"tw": 0, "dt": resp}
***REMOVED***
***REMOVED***"""Abaixo encontra a parte de Database. Depois de resolvido problemas de timestamp, nada fora do normal aqui."""
***REMOVED***def post(self, data):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***INSERT INTO accounts (git_url, ssh_key, priv_key, email, password, heartbeat)
***REMOVED******REMOVED***VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING git_url
***REMOVED******REMOVED***""", (data["git_url"], data["ssh_key"], data["priv_key"], data["email"], data["password"]))
***REMOVED******REMOVED***account_id = cur.fetchone()[0]
***REMOVED******REMOVED***self.conn.commit()

***REMOVED******REMOVED***return {"ok": True, "id": account_id}
***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}

***REMOVED***def get(self, data: dict|None = None):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***if data and "git_id" in data and data["git_id"]:
***REMOVED******REMOVED***cur.execute(
***REMOVED******REMOVED******REMOVED***"SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat "
***REMOVED******REMOVED******REMOVED***"FROM accounts WHERE git_url = %s",
***REMOVED******REMOVED******REMOVED***(data["git_id"],)
***REMOVED******REMOVED***
***REMOVED******REMOVED***else:
***REMOVED******REMOVED***cur.execute("SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat FROM accounts")
***REMOVED******REMOVED***
***REMOVED******REMOVED***rows = cur.fetchall()
***REMOVED******REMOVED***return {"ok": True, "result": [{
***REMOVED******REMOVED******REMOVED***"id": str(r[0]),
***REMOVED******REMOVED******REMOVED***"git_url": r[1],
***REMOVED******REMOVED******REMOVED***"email": r[2],
***REMOVED******REMOVED******REMOVED***"ssh_key": r[3] if data["arg"] else None,
***REMOVED******REMOVED******REMOVED***"priv_key": r[4] if data["arg"] else None,
***REMOVED******REMOVED******REMOVED***"password": r[5],
***REMOVED******REMOVED******REMOVED***"time": r[6],
***REMOVED******REMOVED******REMOVED***"heartbeat": r[7]
***REMOVED******REMOVED***} for r in rows]
***REMOVED******REMOVED***}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}

***REMOVED***def delete(self, data):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("DELETE FROM accounts WHERE git_url= %s RETURNING id", (data["git"],))
***REMOVED******REMOVED***deleted = cur.fetchone()
***REMOVED******REMOVED***self.conn.commit()
***REMOVED******REMOVED***if not deleted:
***REMOVED******REMOVED***return {"ok": False, "func_error": "Conta não encontrada..."}

***REMOVED******REMOVED***return {"ok": True, "id": str(deleted[0])}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
***REMOVED***
***REMOVED***def getpy(self):
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
***REMOVED***
***REMOVED***#Keys necessarias: "edit", "code", "amount", "package" or "change"***REMOVED***  
***REMOVED***def postpy(self, response: dict, vms: list = [], data: list = []): 
***REMOVED***try:
***REMOVED******REMOVED***if not self.getpy()["ok"] and response["edit"]:
***REMOVED******REMOVED***return {"ok": False, "func_error": "Nenhuma dado retornado em code...."}
***REMOVED******REMOVED***
***REMOVED******REMOVED***if not response["edit"]:
***REMOVED******REMOVED***gg = self.get()["result"]
***REMOVED******REMOVED***cur = self.conn.cursor()***REMOVED***
***REMOVED******REMOVED***
***REMOVED******REMOVED***if len(gg) < 0 or len(gg) < int(response["amount"]):
***REMOVED******REMOVED******REMOVED***return {"ok": False, "func_error": f"AmountError: Poucos containers existentes..."}

***REMOVED******REMOVED***for vm in gg:
***REMOVED******REMOVED******REMOVED***None if len(vms) == int(response["amount"]) else vms.append(vm["git_url"])
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED***data.append({
***REMOVED******REMOVED******REMOVED***"code": base64.b64encode(response["code"].encode("utf-8")).decode("utf-8"),
***REMOVED******REMOVED******REMOVED***"package": base64.b64encode(response["package"].encode("utf-8")).decode("utf-8") if response["package"] else None
***REMOVED******REMOVED***})

***REMOVED******REMOVED***data.append({
***REMOVED******REMOVED******REMOVED***"id": "vm_" + i.split(".com:")[1].split(".git")[0],
***REMOVED******REMOVED******REMOVED***"git": i,
***REMOVED******REMOVED******REMOVED***"run": False,
***REMOVED******REMOVED******REMOVED***"data": {
***REMOVED******REMOVED******REMOVED***"error": False,
***REMOVED******REMOVED******REMOVED***"result": "Aguardando resposta....",
***REMOVED******REMOVED******REMOVED***"time": datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")
***REMOVED******REMOVED******REMOVED***}
***REMOVED******REMOVED***} for i in random.sample(vms, k=int(response["amount"])))

***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED******REMOVED***UPDATE container
***REMOVED******REMOVED******REMOVED***SET code = %s
***REMOVED******REMOVED******REMOVED***WHERE id = %s
***REMOVED******REMOVED******REMOVED***""", (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
***REMOVED******REMOVED***
***REMOVED******REMOVED***self.conn.commit()
***REMOVED******REMOVED***return {"ok": True, "result": f"Sucess: Seu codigo estará rodando em {int(response["amount"])} containers!"}

***REMOVED******REMOVED***elif response["edit"]:
***REMOVED******REMOVED***data = self.getpy()["result"]["data"]
***REMOVED******REMOVED***for vms in data[1:]:
***REMOVED******REMOVED******REMOVED***if response["change"]["id"] == vms["id"]:
***REMOVED******REMOVED******REMOVED***vms.update({"run": response["change"]["run"], "data": response["change"]["data"]})
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED******REMOVED******REMOVED***UPDATE container
***REMOVED******REMOVED******REMOVED******REMOVED***SET code = %s
***REMOVED******REMOVED******REMOVED******REMOVED***WHERE id = %s
***REMOVED******REMOVED******REMOVED******REMOVED***""", (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED******REMOVED***self.conn.commit()
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED******REMOVED***return {"ok": True, "result": f"Editado com sucesso! vmid: {response["change"]["id"]}"}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
***REMOVED******REMOVED***
***REMOVED***def getgen(self):
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
***REMOVED***
***REMOVED***#Keys necessarias: "vms", "create" or "del" or "verif"
***REMOVED***def postgen(self, response: dict): 
***REMOVED***try:
***REMOVED******REMOVED***if not self.getgen()["ok"] and not response["create"]:
***REMOVED******REMOVED***return {"ok": False, "func_error": "Nenhuma dado retornado em gen...."}
***REMOVED******REMOVED***
***REMOVED******REMOVED***if response["create"]:
***REMOVED******REMOVED***containers = [item["git_url"] for item in self.get()["result"]]
***REMOVED******REMOVED***data = {
***REMOVED******REMOVED******REMOVED***"create": True,
***REMOVED******REMOVED******REMOVED***"info": {
***REMOVED******REMOVED******REMOVED***"request": int(response["vms"]),
***REMOVED******REMOVED******REMOVED***"created": 0,
***REMOVED******REMOVED******REMOVED***"started": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" ")
***REMOVED******REMOVED******REMOVED***},
***REMOVED******REMOVED******REMOVED***"finished": None
***REMOVED******REMOVED***}
***REMOVED******REMOVED***data["separate"] = self.calculate(containers, int(response["vms"]))
***REMOVED******REMOVED***self.upgen(data)
***REMOVED******REMOVED***return {"ok": True, "All": False, "result": f"Solicitada a criação de {response["vms"]} containers!"}
***REMOVED******REMOVED***
***REMOVED******REMOVED***elif response["del"]:
***REMOVED******REMOVED***data: dict = self.getgen()["result"]["data"]
***REMOVED******REMOVED***if data["info"]["request"] == data["info"]["created"]:
***REMOVED******REMOVED******REMOVED***data.update({"create": False, "finished": self.tempo(data["info"]["started"], datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" "))})
***REMOVED******REMOVED******REMOVED***self.upgen(data)
***REMOVED******REMOVED******REMOVED***return {"ok": True, "All": True, "result": f"Todos containers solicitados já criados!"}
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED***data["info"]["created"] += 1
***REMOVED******REMOVED***self.upgen(data)
***REMOVED******REMOVED***return {"ok": True, "All": False, "result": f"+1 container criado!"}
***REMOVED******REMOVED***
***REMOVED******REMOVED***elif response["verif"]:
***REMOVED******REMOVED***data = self.getgen()["result"]["data"]
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
***REMOVED***def heartbeat(self, data):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***UPDATE accounts
***REMOVED******REMOVED***SET heartbeat = NOW()
***REMOVED******REMOVED***WHERE git_url = %s""", (data["git"],)
***REMOVED******REMOVED***
***REMOVED******REMOVED***self.conn.commit()
***REMOVED******REMOVED***
***REMOVED******REMOVED***if data["node_id"] != self.lastCommit():
***REMOVED******REMOVED***FetchRepo(self.env)
***REMOVED******REMOVED***cont = self.get({"arg": True})["result"]
***REMOVED******REMOVED***for container in cont:
***REMOVED******REMOVED******REMOVED***if container["git_url"] == data["git"]:
***REMOVED******REMOVED******REMOVED***Separate.iniciate(1, self.commit.self_git_push, list(container))
***REMOVED******REMOVED***
***REMOVED******REMOVED***
***REMOVED******REMOVED***return {"ok": True}
***REMOVED***except Exception as e:
***REMOVED******REMOVED***return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
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
***REMOVED******REMOVED******REMOVED***self.delete(i["git_url"])
***REMOVED******REMOVED******REMOVED***
***REMOVED******REMOVED***except Exception as e:
***REMOVED******REMOVED***print("Erro: ", e)

***REMOVED******REMOVED***time.sleep(7)***REMOVED*** 
***REMOVED******REMOVED***
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
***REMOVED******REMOVED******REMOVED***self.distribute()
***REMOVED******REMOVED***else:
***REMOVED******REMOVED******REMOVED***self.trigger = False***REMOVED***
***REMOVED******REMOVED***
***REMOVED******REMOVED***time.sleep(7200)
***REMOVED******REMOVED***
***REMOVED***def distribute(self):
***REMOVED***FetchRepo(self.env)
***REMOVED***cont = self.get({"arg": True})["result"]
***REMOVED***if len(cont) > 0:
***REMOVED******REMOVED***Separate.iniciate(35, self.commit.self_git_push, cont)

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
***REMOVED***
***REMOVED***@staticmethod
***REMOVED***def calculate(containers: list, value: int):
***REMOVED***base = value // len(containers)  
***REMOVED***resto = value % len(containers)  
***REMOVED***resultado = [base] * len(containers)
***REMOVED***
***REMOVED***for i in range(resto):
***REMOVED******REMOVED***resultado[i] += 1
***REMOVED***
***REMOVED***return {
***REMOVED******REMOVED***containers[i]: resultado[i]
***REMOVED******REMOVED***for i in range(len(containers))
***REMOVED***} 