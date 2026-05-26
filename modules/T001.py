from .T005            import Separate
from .T004            import Deployer, FetchRepo
from datetime         import datetime
from zoneinfo         import ZoneInfo
from psycopg2.extras  import Json, DictConnection
import time, psycopg2, random, base64, threading, requests




class GitHub:
    _OWNER = "ErickdeSouza"
    _REPO = "Private-container"
    
    def __init__(self, env, conn: DictConnection|None = None):
        self.env = env
        self.conn = conn
        self.id = "1a1e5709-8e45-4db5-a3c2-3edb8c844ae4"
    
    """Abaixo a parte do Github API. Nova implementacao a essa API devido a necessidade de updates dos containers."""
    def getTable(self):
        try:
            cur = self.conn.cursor()
            cur.execute('SELECT node_id FROM commits WHERE id = %s', (self.id,))
            r = cur.fetchone()
            
            return {"node_id": r[0]} 
        except Exception as e:
            self.conn.rollback()
            return None
    
    def updateTable(self, node_id):
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE commits
            SET node_id = %s
            WHERE id = %s
            """, (node_id, self.id)
        )
        self.conn.commit()
            
    def lastCommit(self):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.env["APPY_GIT_TOKEN"]}",
            "X-GitHub-Api-Version": "2026-03-10"
        }
        resp = requests.get(f"https://api.github.com/repos/{GitHub._OWNER}/{GitHub._REPO}/commits", headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()[0]["node_id"]
            return data

        return None
    
    def getcommit(self):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.env["APPY_GIT_TOKEN"]}",
            "X-GitHub-Api-Version": "2026-03-10"
        }
        resp = requests.get(f"https://api.github.com/repos/{GitHub._OWNER}/{GitHub._REPO}/commits", headers=headers)
        
        if resp.status_code == 200:
            return resp.json()[0]
        
        return None
    

class MainAPI(GitHub):
    def __init__(self, env, test: bool|None = None):
        self.conn = psycopg2.connect(env["APPY_DB_URL"], sslmode="require")
        super().__init__(env, self.conn)
        self.commit = Deployer()
        #payload requerido na resposta recebida pelo user
        self.required = ["tw", "dt"]
        self.twcodes = [
            [i for i in range(1, 7)],
            (1, [self.getgen, self.postgen]),
            (2, [self.getpy, self.postpy]),
            (3, self.heartbeat),
            (4, self.get),
            (5, self.post),
            (6, self.delete) 
        ]
        if not test:
            threading.Thread(target=self.verifVm).start()
            threading.Thread(target=self.verifyC).start()
        
    def manager(self, data: dict):
        #verify do payload
        for item in self.required:
            if item not in data.keys():
                return {"error": f'"{item}" está faltando no seu body.'}
            
        if data["tw"] not in self.twcodes[0]:
            return {"error": 'O código do seu "tw" não existe ou é invalido.'}
        
        for code, func in self.twcodes[1:]:
            if callable(func) and code == data["tw"]:
                return func(data["dt"])
            
            elif not callable(func) and code == data["tw"]:
                if "method" not in data["dt"]:
                    return {"error": '"method" em falta em seu body.'}
                
                method = data["dt"]["method"]
                if type(method) == str and method == "get":
                    return func[0](data["dt"])
                elif type(method) == str and method == "post":
                    return func[1](data["dt"])
                else:
                    return {"error": '"method" só aceita "post" ou "get" no body.'}
                
    def response(self, data):
        resp = self.manager(data)
        if not resp:
            return {"tw": 67, "dt": {"error": 'Alguma coisa deu errado...'}}
        return {"tw": 0, "dt": resp}
    
    """Abaixo encontra a parte de Database. Depois de resolvido problemas de timestamp, nada fora do normal aqui."""
    def post(self, data):
        try:
            cur = self.conn.cursor()
            cur.execute("""
            INSERT INTO accounts (git_url, ssh_key, priv_key, email, password, heartbeat)
            VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING git_url
            """, (data["git_url"], data["ssh_key"], data["priv_key"], data["email"], data["password"]))
            account_id = cur.fetchone()[0]
            self.conn.commit()

            return {"ok": True, "id": account_id}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}

    def get(self, data: dict|None = None):
        try:
            cur = self.conn.cursor()
            if data and "git_url" in data and data["git_url"]:
                cur.execute(
                    "SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat "
                    "FROM accounts WHERE git_url = %s",
                    (data["git_url"],)
                )
            else:
                cur.execute("SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat FROM accounts")
            
            git = self.getcommit()
            rows = cur.fetchall()
            return {"ok": True, "result": [{
                    "id": str(r[0]),
                    "git_url": r[1],
                    "email": r[2],
                    "ssh_key": r[3] if data and data["arg"] else None,
                    "priv_key": r[4] if data and data["arg"] else None,
                    "password": r[5],
                    "time": r[6],
                    "heartbeat": r[7]
                } for r in rows],
                "commit": git["commit"]["message"] if git else None,
                "lastrepo": git["commit"]["committer"]["date"] if git else None
            }

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}

    def delete(self, data):
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM accounts WHERE git_url= %s RETURNING id", (data["git_url"],))
            deleted = cur.fetchone()
            self.conn.commit()
            if not deleted:
                return {"ok": False, "func_error": "Conta não encontrada..."}

            return {"ok": True, "id": str(deleted[0])}

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
    
    def getpy(self, data=None):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT code 
                FROM container WHERE id = %s""", ("2b66698d-4995-410a-9a7d-3a462b25e323",)
            )
            
            r = cur.fetchone()
            return {"ok": True, "result": r[0]}

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
    
    #Keys necessarias: "edit", "code", "amount", "package" or "change"      
    def postpy(self, response: dict, vms: list = [], data: list = []): 
        try:
            if not self.getpy()["ok"] and response["edit"]:
                return {"ok": False, "func_error": "Nenhuma dado retornado em code...."}
            
            if not response["edit"]:
                gg = self.get()["result"]  
                
                if len(gg) < 0 or len(gg) < int(response["amount"]):
                    return {"ok": False, "func_error": f"AmountError: Poucos containers existentes..."}

                for vm in gg:
                    None if len(vms) == int(response["amount"]) else vms.append(vm["git_url"])
                        
                data.append({
                    "code": base64.b64encode(response["code"].encode("utf-8")).decode("utf-8"),
                    "package": base64.b64encode(response["package"].encode("utf-8")).decode("utf-8") if response["package"] else None
                })

                data.append({
                    "id": "vm_" + i.split(".com:")[1].split(".git")[0],
                    "git": i,
                    "run": False,
                    "data": {
                        "error": False,
                        "result": "Aguardando resposta....",
                        "time": datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")
                    }
                } for i in random.sample(vms, k=int(response["amount"])))
                
                self.uppy(data)
                return {"ok": True, "result": f"Sucess: Seu codigo estará rodando em {int(response["amount"])} containers!"}

            elif response["edit"]:
                data = self.getpy()["result"]["data"]
                for vms in data[1:]:
                    if response["change"]["id"] == vms["id"]:
                        vms.update({"run": response["change"]["run"], "data": response["change"]["data"]})
                        self.uppy(data)
                        return {"ok": True, "result": f"Editado com sucesso! vmid: {response["change"]["id"]}"}

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
        
    def uppy(self, data):
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE container
            SET code = %s
            WHERE id = %s
            """, (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
        )
        self.conn.commit()
            
    def getgen(self, data=None):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT gen 
                FROM container WHERE id = %s""", ("2b66698d-4995-410a-9a7d-3a462b25e323",)
            )
            r = cur.fetchone()
            
            if data and data["verif"]:
                resp = r[0]["data"]
                if resp["info"]["request"] == resp["info"]["created"]:
                    return {"ok": True, "result": f"Todos containers solicitados já criados!"}
                
                return {"ok": True, "result": f"{resp["info"]["created"]} containers criados no momento."}
            
            return {"ok": True, "result": r[0]}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
        
    #Keys necessarias: "vms", "create" or "del" or "verif"
    def postgen(self, response: dict): 
        try:
            if not self.getgen()["ok"] and response["del"]:
                return {"ok": False, "func_error": "Nenhuma dado retornado em gen...."}
            
            if "create" in response and response["create"]:
                revms = int(response["vms"])
                containers = [item["git_url"] for item in self.get()["result"]]
                data = {
                    "create": True,
                    "info": {
                        "request": revms if revms > 0 else 1,
                        "created": 0,
                        "started": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" ")
                    },
                    "finished": None
                }
                data["separate"] = self.calculate(containers, int(response["vms"]))
                self.upgen(data)
                return {"ok": True, "All": False, "result": f"Solicitada a criação de {response["vms"]} containers!"}
                
            elif "del" in response and response["del"]:
                data: dict = self.getgen()["result"]["data"]
                if data["info"]["request"] == data["info"]["created"]:
                    data.update({"create": False, "finished": self.tempo(data["info"]["started"], datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" "))})
                    self.upgen(data)
                    return {"ok": True, "All": True, "result": f"Todos containers solicitados já criados!"}
                    
                data["info"]["created"] += 1
                data["separate"][response["git"]] -= 1
                self.upgen(data)
                return {"ok": True, "All": False, "result": f"+1 container criado!"}
            
            
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
        
    def upgen(self, data):
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE container
            SET gen = %s
            WHERE id = %s
            """, (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
        )
        self.conn.commit()
    
    def heartbeat(self, data):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE accounts
                SET heartbeat = NOW()
                WHERE git_url = %s""", (data["git_url"],)
            )
            self.conn.commit()
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "func_error": f"Retornou o erro: {str(e)}"}
        
    def verifVm(self):
        while True:
            try:
                data = self.get()
                if not data["ok"]:
                    print(data["func_error"])
                    time.sleep(60) 
                    continue
                
                for i in data["result"]:
                    timestamp = datetime.fromisoformat(str(i["heartbeat"]))
                    if timestamp.tzinfo is not None:
                        timestamp = timestamp.replace(tzinfo=None)

                    agora = datetime.now()
                    diff = (agora - timestamp).total_seconds()

                    if diff >= 3600:
                        self.delete({"git": i["git_url"]})
                        
            except Exception as e:
                print("Erro: ", e)

            time.sleep(7)     
            
    def verifyC(self):
        while True:
            last_commit = self.lastCommit()
            table = self.getTable()
            if last_commit and table and table["node_id"] != "Wait":
                if last_commit != table["node_id"]:
                    self.trigger = True
                    self.updateTable(last_commit)
                    self.distribute()
            
            time.sleep(3600)
            
    def distribute(self):
        FetchRepo(self.env)
        cont = self.get({"arg": True})["result"]
        if len(cont) > 0:
            Separate.iniciate(35, self.commit.self_git_push, cont)

    @staticmethod
    def tempo(ts_inicio: str, ts_fim: str):
        inicio = datetime.fromisoformat(ts_inicio)
        fim = datetime.fromisoformat(ts_fim)

        total_segundos = int((fim - inicio).total_seconds())

        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60

        if horas > 0:
            return f"{horas} horas e {minutos} minutos"
        else:
            return f"{minutos} minutos"
        
    @staticmethod
    def calculate(containers: list, value: int):
        base = value // len(containers)  
        resto = value % len(containers)  
        resultado = [base] * len(containers)
        
        for i in range(resto):
            resultado[i] += 1
        
        return {
            containers[i]: resultado[i]
            for i in range(len(containers))
        } 