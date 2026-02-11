from datetime import datetime
from zoneinfo import ZoneInfo
from psycopg2.extras import Json
import time, psycopg2, random, base64, threading



class FetchData:
    def __init__(self, env):
        self.conn = psycopg2.connect(env["APPY_DB_URL"], sslmode="require")
        threading.Thread(target=self.verifVm).start()
        
    def tempo(self, ts_inicio: str, ts_fim: str):
        inicio = datetime.fromisoformat(ts_inicio)
        fim = datetime.fromisoformat(ts_fim)

        total_segundos = int((fim - inicio).total_seconds())

        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60

        if horas > 0:
            return f"{horas} horas e {minutos} minutos"
        else:
            return f"{minutos} minutos"

    def post(self, d):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                        INSERT INTO accounts (git_url, ssh_key, priv_key, email, password)
                        VALUES (%s, %s, %s, %s, %s) RETURNING git_url
                        """, (d["git_url"], d["ssh_key"], d["priv_key"], d["email"], d["password"]))
            account_id = cur.fetchone()[0]
            self.conn.commit()

            return {"ok": True, "id": account_id}
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "error": f"Retornou o erro: {str(e)}"}

    def get(self, git_id: str = None, arg: bool = False):
        try:
            cur = self.conn.cursor()
            if git_id:
                cur.execute(
                    "SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat "
                    "FROM accounts WHERE git_url = %s",
                    (git_id,)
                )
                r = cur.fetchone()
                return {"ok": True, "result": {
                        "id": str(r[0]),
                        "git_url": r[1],
                        "email": r[2],
                        "ssh_key": r[3] if arg else None,
                        "priv_key": r[4] if arg else None,
                        "password": r[5],
                        "time": r[6],
                        "heartbeat": r[7]
                    }
                }

            cur.execute("SELECT id, git_url, email, ssh_key, priv_key, password, created_at, heartbeat FROM accounts")
            rows = cur.fetchall()

            return {"ok": True, "result": [{
                    "id": str(r[0]),
                    "git_url": r[1],
                    "email": r[2],
                    "ssh_key": r[3] if arg else None,
                    "priv_key": r[4] if arg else None,
                    "password": r[5],
                    "time": r[6],
                    "heartbeat": r[7]
                } for r in rows]
            }

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "error": f"Retornou o erro: {str(e)}"}

    def delete(self, git):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "DELETE FROM accounts WHERE git_url= %s RETURNING id",
                (git,)
            )
            deleted = cur.fetchone()
            self.conn.commit()
            if not deleted:
                return {"ok": False, "error": "Conta não encontrada..."}

            return {"ok": True, "id": str(deleted[0])}

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
    
    def fcode(self):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT code 
                FROM container WHERE id = %s
            """, ("2b66698d-4995-410a-9a7d-3a462b25e323",)
            )
            r = cur.fetchone()
            return {"ok": True, "result": r[0]}

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
            
    def pcode(
        self,
        response: dict, #Keys necessarias: "edit", "code", "amount", "package" or "change"
    ):
        try:
            if not self.fcode()["ok"] and response["edit"]:
                return {"ok": False, "error": "Nenhuma dado retornado em code...."}
            
            if not response["edit"]:
                vms = []
                data = []
                gg = self.get()["result"]
                cur = self.conn.cursor()

                data_str = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")
                amount = int(response["amount"])

                if len(gg) < 0 or len(gg) < amount:
                    return {
                        "ok": False,
                        "error": f"AmountError: Poucos containers existentes..."
                    }

                for vm in gg:
                    if len(vms) == amount:
                        break
                    vms.append(vm["git_url"])

                data.append({
                    "code": base64.b64encode(response["code"].encode("utf-8")).decode("utf-8"),
                    "package": base64.b64encode(response["package"].encode("utf-8")).decode("utf-8") if response["package"] else None
                })

                samplevm = random.sample(vms, k=amount)
                for i in samplevm:
                    data.append({
                        "id": "vm_" + i.split(".com:")[1].split(".git")[0],
                        "git": i,
                        "run": False,
                        "data": {
                            "error": False,
                            "result": "Aguardando resposta....",
                            "time": data_str
                        }
                    })


                cur = self.conn.cursor()
                cur.execute("""
                    UPDATE container
                    SET code = %s
                    WHERE id = %s
                    """, (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
                )
                self.conn.commit()

                return {
                    "ok": True,
                    "result": f"Sucess: Seu codigo estará rodando em {amount} containers!"
                }


            elif response["edit"]:
                data = self.fcode()["result"]["data"]
                resp = response["change"]

                for vms in data[1:]:
                    if resp["id"] == vms["id"]:
                        vms.update({"run": resp["run"], "data": resp["data"]})

                        cur = self.conn.cursor()
                        cur.execute("""
                            UPDATE container
                            SET code = %s
                            WHERE id = %s
                            """, (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
                        )
                        self.conn.commit()

                        return {
                            "ok": True,
                            "result": f"Editado com sucesso! vmid: {resp["id"]}"
                        }

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
            
    def fgen(self):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT gen 
                FROM container WHERE id = %s
            """, ("2b66698d-4995-410a-9a7d-3a462b25e323",)
            )
            r = cur.fetchone()
            return {"ok": True, "result": r[0]}

        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "error": f"Retornou o erro: {str(e)}"}

    def pgen(
        self,
        response: dict, #Keys necessarias: "vms", "create" or "del" or "verif"
    ):
        try:
            if not self.fgen()["ok"] and not response["create"]:
                return {"ok": False, "error": "Nenhuma dado retornado em gen...."}
            
            if response["create"]:
                data = {
                    "create": True,
                    "info": {
                        "request": int(response["vms"]),
                        "created": 0,
                        "started": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" ")
                    },
                    "finished": None
                }
                self.upgen(data)
                return {"ok": True, "All": False, "result": f"Solicitada a criação de {response["vms"]} containers!"}
                
            elif response["del"]:
                data = self.fgen()["result"]["data"]
                if data["info"]["request"] == data["info"]["created"]:
                    lol = self.tempo(data["info"]["started"], datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(sep=" "))
                    data.update({"create": False, "finished": lol})
                    self.upgen(data)
                    return {"ok": True, "All": True, "result": f"Todos containers solicitados já criados!"}
                    
                data["info"]["created"] += 1
                self.upgen(data)
                return {"ok": True, "All": False, "result": f"+1 container criado!"}
            
            elif response["verif"]:
                data = self.fgen()["result"]["data"]
                if data["info"]["request"] == data["info"]["created"]:
                    return {"ok": True, "result": f"Todos containers solicitados já criados!"}
                
                return {"ok": True, "result": f"{data["info"]["created"]} containers criados no momento."}
            
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
        
    def upgen(self, data):
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE container
            SET gen = %s
            WHERE id = %s
            """, (Json({"data": data}), "2b66698d-4995-410a-9a7d-3a462b25e323")
        )
        self.conn.commit()
    
    def upcontainer(self, git):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE accounts
                SET heartbeat = NOW() AT TIME ZONE 'America/Sao_Paulo'
                WHERE git_url = %s
            """, (git,))
            self.conn.commit()
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": f"Retornou o erro: {str(e)}"}
        
    def verifVm(self):
        while True:
            try:
                data = self.get()["result"]
                if len(data) > 0:
                    for i in data:
                        timestamp_br = datetime.fromisoformat(i["heartbeat"])
                        if timestamp_br.tzinfo is None:
                            timestamp_br = timestamp_br.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
                        agora_br = datetime.now(ZoneInfo("America/Sao_Paulo"))
                        diff = (agora_br - timestamp_br).total_seconds()

                        if diff >= 10 * 60:
                            print("deletado")
                            self.delete(i["git_url"])
            except Exception:
                pass
            time.sleep(7)