***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***

class ScalingoDeployer:
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***


***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***"ssh-keyscan", "ssh.osc-fr1.scalingo.com"],
***REMOVED******REMOVED***stdout=known_hosts.open("w"),
***REMOVED******REMOVED***stderr=subprocess.DEVNULL,
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***public_key = key_path.with_suffix(".pub").read_text(encoding="utf-8")
***REMOVED***private_key = key_path.read_text(encoding="utf-8")
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***return public_key, private_key, key_path, known_hosts
***REMOVED***
***REMOVED***def temp_ssh_update(self, priv, pub):
***REMOVED***self.self_temp_dir = Path(
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***key_path = self.self_temp_dir / "id_ed25519"
***REMOVED***known_hosts = self.self_temp_dir / "known_hosts"
***REMOVED***public_key_path = self.self_temp_dir / "id_ed25519.pub"
***REMOVED***
***REMOVED***key_path.write_text(priv, encoding="utf-8")
***REMOVED***public_key_path.write_text(pub, encoding="utf-8")
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***"ssh-keyscan", "ssh.osc-fr1.scalingo.com"],
***REMOVED******REMOVED***stdout=known_hosts.open("w"),
***REMOVED******REMOVED***stderr=subprocess.DEVNULL,
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***return key_path, known_hosts, self.self_temp_dir
***REMOVED***
***REMOVED***def git_push_holder(
***REMOVED***self,
***REMOVED***key_path: Path,
***REMOVED***known_hosts: Path,
***REMOVED***remote_name: str,
***REMOVED***remote_url: str,
***REMOVED***branch: str,
***REMOVED***commit_message: str,
***REMOVED***temp_dir = None
***REMOVED***):
***REMOVED***if not temp_dir:
***REMOVED******REMOVED***temp_dir = self.temp_dir

***REMOVED***try:
***REMOVED******REMOVED***repo = Repo.init(REPO_PATH)

***REMOVED******REMOVED***ssh_cmd = (
***REMOVED******REMOVED***f"ssh -i {key_path.as_posix()} "
***REMOVED******REMOVED***"-o IdentitiesOnly=yes "
***REMOVED******REMOVED***"-o StrictHostKeyChecking=no "
***REMOVED******REMOVED***f"-o UserKnownHostsFile={known_hosts.as_posix()}"
***REMOVED******REMOVED***

***REMOVED******REMOVED***# força git usar esse ssh
***REMOVED******REMOVED***repo.git.config(
***REMOVED******REMOVED***"--local",
***REMOVED******REMOVED***"--add",
***REMOVED******REMOVED***"core.sshCommand",
***REMOVED******REMOVED***ssh_cmd,
***REMOVED******REMOVED***

***REMOVED******REMOVED***for r in list(repo.remotes):
***REMOVED******REMOVED***repo.delete_remote(r)

***REMOVED******REMOVED***repo.create_remote(remote_name, remote_url)


***REMOVED******REMOVED***repo.git.add(A=True)
***REMOVED******REMOVED***
***REMOVED******REMOVED***repo.index.commit(commit_message)

***REMOVED******REMOVED***try:
***REMOVED******REMOVED***repo.git.fetch("--unshallow")
***REMOVED******REMOVED***except Exception:
***REMOVED******REMOVED***pass

***REMOVED******REMOVED***repo.git.push(
***REMOVED******REMOVED***"--force",
***REMOVED******REMOVED***remote_name,
***REMOVED******REMOVED***f"HEAD:{branch}",
***REMOVED******REMOVED***

***REMOVED******REMOVED***print("pushado com sucesso!")

***REMOVED***finally:
***REMOVED******REMOVED***if temp_dir and temp_dir.exists():
***REMOVED******REMOVED***shutil.rmtree(temp_dir, ignore_errors=True)
***REMOVED******REMOVED***
***REMOVED***def git_push(self, key_path: Path, known_hosts: Path, remote_name: str, remote_url: str, branch: str = "master", commit_message: str = "fvck yall"):
***REMOVED***self.git_push_holder(key_path, known_hosts, remote_name, remote_url, branch, commit_message)
***REMOVED***
***REMOVED***def self_git_push(self, data, remote_name: str = "production", branch: str = "master", commit_message: str = "fvck yall"):
***REMOVED***key_path, known_hosts = self.temp_ssh_update(data["priv_key"], data["ssh_key"])
***REMOVED***self.git_push_holder(key_path, known_hosts, remote_name, data["git_url"], branch, commit_message, self.self_temp_dir)

***REMOVED***def del_ssh(self):
***REMOVED***if self.temp_dir and self.temp_dir.exists():
***REMOVED******REMOVED***shutil.rmtree(self.temp_dir, ignore_errors=True)
***REMOVED******REMOVED***

***REMOVED***
***REMOVED***def __init__(self, env):
***REMOVED***self.api_clone_repo(
***REMOVED******REMOVED***token=env["APPY_GIT_TOKEN"],
***REMOVED******REMOVED***owner="ErickdeSouza",
***REMOVED******REMOVED***repo="Private-container",
***REMOVED******REMOVED***dest_folder=REPO_PATH
***REMOVED***

***REMOVED***def api_clone_repo(
***REMOVED***self,
***REMOVED***token,
***REMOVED***owner,
***REMOVED***repo,
***REMOVED***dest_folder: Path,
***REMOVED***branch="main"
***REMOVED***):
***REMOVED***url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"

***REMOVED***headers = {
***REMOVED******REMOVED***"Authorization": f"Bearer {token}",
***REMOVED******REMOVED***"Accept": "application/vnd.github+json"
***REMOVED***}

***REMOVED***response = requests.get(url, headers=headers)
***REMOVED***response.raise_for_status()

***REMOVED***temp_extract_path = dest_folder.parent / f"{dest_folder.name}_temp"

***REMOVED***if temp_extract_path.exists():
***REMOVED******REMOVED***shutil.rmtree(temp_extract_path)

***REMOVED***temp_extract_path.mkdir(parents=True, exist_ok=True)

***REMOVED***with zipfile.ZipFile(io.BytesIO(response.content)) as z:
***REMOVED******REMOVED***z.extractall(temp_extract_path)

***REMOVED***inner_folder = next(temp_extract_path.iterdir())

***REMOVED***if dest_folder.exists():
***REMOVED******REMOVED***shutil.rmtree(dest_folder)

***REMOVED***shutil.move(str(inner_folder), str(dest_folder))
***REMOVED***shutil.rmtree(temp_extract_path)

***REMOVED***git_folder = dest_folder / ".git"
***REMOVED***if git_folder.exists():
***REMOVED******REMOVED***shutil.rmtree(git_folder)
***REMOVED******REMOVED***
***REMOVED***for filename in ["Aptfile", ".buildpacks"]:
***REMOVED******REMOVED***file_path = dest_folder / filename
***REMOVED******REMOVED***if file_path.exists():
***REMOVED******REMOVED***if file_path.is_dir():
***REMOVED******REMOVED******REMOVED***shutil.rmtree(file_path)
***REMOVED******REMOVED***else:
***REMOVED******REMOVED******REMOVED***file_path.unlink()
***REMOVED******REMOVED******REMOVED***
***REMOVED***b = requests.get("https://raw.githubusercontent.com/ErickdeSouza/easy/refs/heads/main/builpack").text
***REMOVED***l = requests.get("https://raw.githubusercontent.com/ErickdeSouza/easy/refs/heads/main/libs").text
***REMOVED***
***REMOVED***with open(dest_folder / "Aptfile", "w", encoding="utf-8") as f:
***REMOVED******REMOVED***for i in l.splitlines():
***REMOVED******REMOVED***f.write(i + "\n")
***REMOVED******REMOVED***
***REMOVED***with open(dest_folder / ".buildpacks", "w", encoding="utf-8") as f:
***REMOVED******REMOVED***for i in b.splitlines():
***REMOVED******REMOVED***f.write(i + "\n")