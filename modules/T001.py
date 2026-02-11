from datetime import datetime
from zoneinfo import ZoneInfo
from psycopg2.extras import Json
import time, psycopg2, random, base64, threading



class FetchData:
***REMOVED***def __init__(self, env):
***REMOVED***self.conn = psycopg2.connect(env["APPY_DB_URL"], sslmode="require")
***REMOVED***threading.Thread(target=self.verifVm).start()
***REMOVED***
***REMOVED***def tempo(self, ts_inicio: str, ts_fim: str):
***REMOVED***inicio = datetime.fromisoformat(ts_inicio)
***REMOVED***fim = datetime.fromisoformat(ts_fim)

***REMOVED***total_segundos = int((fim - inicio).total_seconds())

***REMOVED***horas = total_segundos // 3600
***REMOVED***minutos = (total_segundos % 3600) // 60

***REMOVED***if horas > 0:
***REMOVED******REMOVED***return f"{horas} horas e {minutos} minutos"
***REMOVED***else:
***REMOVED******REMOVED***return f"{minutos} minutos"

***REMOVED***def post(self, d):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED******REMOVED***INSERT INTO accounts (git_url, ssh_key, priv_key, email, password)
***REMOVED******REMOVED******REMOVED***VALUES (%s, %s, %s, %s, %s) RETURNING git_url
***REMOVED******REMOVED******REMOVED***""", (d["git_url"], d["ssh_key"], d["priv_key"], d["email"], d["password"]))
***REMOVED******REMOVED***account_id = cur.fetchone()[0]
***REMOVED******REMOVED***self.conn.commit()

***REMOVED******REMOVED***return {"ok": True, "id": account_id}
***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "error": f"Retornou o erro: {str(e)}"}

***REMOVED***def get(self, git_id: str = None, arg: bool = False):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***if git_id:
***REMOVED******REMOVED***cur.execute(
***REMOVED******REMOVED******REMOVED***"SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat "
***REMOVED******REMOVED******REMOVED***"FROM accounts WHERE git_url = %s",
***REMOVED******REMOVED******REMOVED***(git_id,)
***REMOVED******REMOVED***
***REMOVED******REMOVED***r = cur.fetchone()
***REMOVED******REMOVED***return {"ok": True, "result": {
***REMOVED******REMOVED******REMOVED***"id": str(r[0]),
***REMOVED******REMOVED******REMOVED***"git_url": r[1],
***REMOVED******REMOVED******REMOVED***"email": r[2],
***REMOVED******REMOVED******REMOVED***"ssh_key": r[3] if arg else None,
***REMOVED******REMOVED******REMOVED***"priv_key": r[4] if arg else None,
***REMOVED******REMOVED******REMOVED***"password": r[5],
***REMOVED******REMOVED******REMOVED***"time": r[6],
***REMOVED******REMOVED******REMOVED***"heartbeat": r[7]
***REMOVED******REMOVED******REMOVED***}
***REMOVED******REMOVED***}

***REMOVED******REMOVED***cur.execute("SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat FROM accounts")
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
***REMOVED******REMOVED***return {"ok": False, "error": f"Retornou o erro: {str(e)}"}

***REMOVED***def delete(self, git):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute(
***REMOVED******REMOVED***"DELETE FROM accounts WHERE git_url= %s RETURNING id",
***REMOVED******REMOVED***(git,)
***REMOVED******REMOVED***
***REMOVED******REMOVED***deleted = cur.fetchone()
***REMOVED******REMOVED***self.conn.commit()
***REMOVED******REMOVED***if not deleted:
***REMOVED******REMOVED***return {"ok": False, "error": "Conta não encontrada..."}

***REMOVED******REMOVED***return {"ok": True, "id": str(deleted[0])}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
***REMOVED***
***REMOVED***def fcode(self):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***SELECT code 
***REMOVED******REMOVED***FROM container WHERE id = %s
***REMOVED******REMOVED***""", ("2b66698d-4995-410a-9a7d-3a462b25e323",)
***REMOVED******REMOVED***
***REMOVED******REMOVED***r = cur.fetchone()
***REMOVED******REMOVED***return {"ok": True, "result": r[0]}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
***REMOVED******REMOVED***
***REMOVED***def pcode(
***REMOVED***self,
***REMOVED***response: dict, #Keys necessarias: "edit", "code", "amount", "package" or "change"
***REMOVED***):
***REMOVED***try:
***REMOVED******REMOVED***if not self.fcode()["ok"] and response["edit"]:
***REMOVED******REMOVED***return {"ok": False, "error": "Nenhuma dado retornado em code...."}
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
***REMOVED******REMOVED******REMOVED***"error": f"AmountError: Poucos containers existentes..."
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
***REMOVED******REMOVED***return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
***REMOVED******REMOVED***
***REMOVED***def fgen(self):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***SELECT gen 
***REMOVED******REMOVED***FROM container WHERE id = %s
***REMOVED******REMOVED***""", ("2b66698d-4995-410a-9a7d-3a462b25e323",)
***REMOVED******REMOVED***
***REMOVED******REMOVED***r = cur.fetchone()
***REMOVED******REMOVED***return {"ok": True, "result": r[0]}

***REMOVED***except Exception as e:
***REMOVED******REMOVED***self.conn.rollback()
***REMOVED******REMOVED***return {"ok": False, "error": f"Retornou o erro: {str(e)}"}

***REMOVED***def pgen(
***REMOVED***self,
***REMOVED***response: dict, #Keys necessarias: "vms", "create" or "del" or "verif"
***REMOVED***):
***REMOVED***try:
***REMOVED******REMOVED***if not self.fgen()["ok"] and not response["create"]:
***REMOVED******REMOVED***return {"ok": False, "error": "Nenhuma dado retornado em gen...."}
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
***REMOVED******REMOVED***return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
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
***REMOVED***def upcontainer(self, git):
***REMOVED***try:
***REMOVED******REMOVED***cur = self.conn.cursor()
***REMOVED******REMOVED***cur.execute("""
***REMOVED******REMOVED***UPDATE accounts
***REMOVED******REMOVED***SET heartbeat = NOW() AT TIME ZONE 'America/Sao_Paulo'
***REMOVED******REMOVED***WHERE git_url = %s
***REMOVED******REMOVED***""", (git,))
***REMOVED******REMOVED***self.conn.commit()
***REMOVED******REMOVED***
***REMOVED******REMOVED***return {"ok": True}
***REMOVED***except Exception as e:
***REMOVED******REMOVED***return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
***REMOVED***
***REMOVED***def verifVm(self):
***REMOVED***while True:
***REMOVED******REMOVED***try:
***REMOVED******REMOVED***data = self.get()["result"]
***REMOVED******REMOVED***if len(data) > 0:
***REMOVED******REMOVED******REMOVED***for i in data:
***REMOVED******REMOVED******REMOVED***timestamp_br = datetime.fromisoformat(str(i["heartbeat"]))
***REMOVED******REMOVED******REMOVED***if timestamp_br.tzinfo is None:
***REMOVED******REMOVED******REMOVED******REMOVED***timestamp_br = timestamp_br.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
***REMOVED******REMOVED******REMOVED***agora_br = datetime.now(ZoneInfo("America/Sao_Paulo"))
***REMOVED******REMOVED******REMOVED***diff = (agora_br - timestamp_br).total_seconds()

***REMOVED******REMOVED******REMOVED***if diff >= 10 * 60:
***REMOVED******REMOVED******REMOVED******REMOVED***print("deletado")
***REMOVED******REMOVED******REMOVED******REMOVED***self.delete(i["git_url"])
***REMOVED******REMOVED***except Exception:
***REMOVED******REMOVED***pass
***REMOVED******REMOVED***time.sleep(7)