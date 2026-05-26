from pathlib  import Path
from git      import Repo
import subprocess, tempfile, shutil, os, requests, zipfile, io

BASE_DIR = Path(__file__).resolve().parent
REPO_PATH = BASE_DIR / "commit"

class Deployer:
    def __init__(self):
        self.temp_dir: Path | None = None
        self.self_temp_dir: Path | None = None

    def temp_ssh(self, comment="temp-deploy-key"):
        self.temp_dir = Path(
            tempfile.mkdtemp(dir=BASE_DIR / "ssh", prefix="sshkey_")
        )

        key_path = self.temp_dir / "id_ed25519"
        known_hosts = self.temp_dir / "known_hosts"
        public_key_path = self.temp_dir / "id_ed25519.pub"


        subprocess.run(
            [
                "ssh-keygen",
                "-t", "ed25519",
                "-f", str(key_path),
                "-N", "",
                "-C", comment,
            ],
            check=True,
        )

        os.chmod(key_path, 0o600)
        os.chmod(public_key_path, 0o644)
        
        subprocess.run(
            ["ssh-keyscan", "ssh.osc-fr1.scalingo.com"],
            stdout=known_hosts.open("w"),
            stderr=subprocess.DEVNULL,
            check=True,
        )
        
        public_key = key_path.with_suffix(".pub").read_text(encoding="utf-8")
        private_key = key_path.read_text(encoding="utf-8")
        
        
        
        return public_key, private_key, key_path, known_hosts
    
    def temp_ssh_update(self, priv, pub):
        self.self_temp_dir = Path(
            tempfile.mkdtemp(dir=BASE_DIR / "ssh", prefix="sshkey_")
        )
        
        key_path = self.self_temp_dir / "id_ed25519"
        known_hosts = self.self_temp_dir / "known_hosts"
        public_key_path = self.self_temp_dir / "id_ed25519.pub"
        
        key_path.write_text(priv, encoding="utf-8")
        public_key_path.write_text(pub, encoding="utf-8")
        
        os.chmod(key_path, 0o600)
        os.chmod(public_key_path, 0o644)
        
        subprocess.run(
            ["ssh-keyscan", "ssh.osc-fr1.scalingo.com"],
            stdout=known_hosts.open("w"),
            stderr=subprocess.DEVNULL,
            check=True,
        )
        
        return key_path, known_hosts, self.self_temp_dir
        
    def git_push_holder(
        self,
        key_path: Path,
        known_hosts: Path,
        remote_name: str,
        remote_url: str,
        branch: str,
        commit_message: str,
        temp_dir = None
    ):
        if not temp_dir:
            temp_dir = self.temp_dir

        try:
            repo = Repo.init(REPO_PATH)

            ssh_cmd = (
                f"ssh -i {key_path.as_posix()} "
                "-o IdentitiesOnly=yes "
                "-o StrictHostKeyChecking=no "
                f"-o UserKnownHostsFile={known_hosts.as_posix()}"
            )

            # força git usar esse ssh
            repo.git.config(
                "--local",
                "--add",
                "core.sshCommand",
                ssh_cmd,
            )

            for r in list(repo.remotes):
                repo.delete_remote(r)

            repo.create_remote(remote_name, remote_url)


            repo.git.add(A=True)
            
            repo.index.commit(commit_message)

            try:
                repo.git.fetch("--unshallow")
            except Exception:
                pass

            repo.git.push(
                "--force",
                remote_name,
                f"HEAD:{branch}",
            )

            print("pushado com sucesso!")

        finally:
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
                
    def git_push(self, key_path: Path, known_hosts: Path, remote_name: str, remote_url: str, branch: str = "master", commit_message: str = "fvck yall"):
        self.git_push_holder(key_path, known_hosts, remote_name, remote_url, branch, commit_message)
        
    def self_git_push(self, data, remote_name: str = "production", branch: str = "master", commit_message: str = "fvck yall"):
        key_path, known_hosts = self.temp_ssh_update(data["priv_key"], data["ssh_key"])
        self.git_push_holder(key_path, known_hosts, remote_name, data["git_url"], branch, commit_message, self.self_temp_dir)

    def del_ssh(self):
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            

class FetchRepo:
    def __init__(self, env):
        self.api_clone_repo(
            token=env["APPY_GIT_TOKEN"],
            owner="ErickdeSouza",
            repo="Private-container",
            dest_folder=REPO_PATH
        )

    def api_clone_repo(
        self,
        token,
        owner,
        repo,
        dest_folder: Path,
        branch="main"
    ):
        url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        temp_extract_path = dest_folder.parent / f"{dest_folder.name}_temp"

        if temp_extract_path.exists():
            shutil.rmtree(temp_extract_path)

        temp_extract_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(temp_extract_path)

        inner_folder = next(temp_extract_path.iterdir())

        if dest_folder.exists():
            shutil.rmtree(dest_folder)

        shutil.move(str(inner_folder), str(dest_folder))
        shutil.rmtree(temp_extract_path)

        git_folder = dest_folder / ".git"
        if git_folder.exists():
            shutil.rmtree(git_folder)
            
        for filename in ["Aptfile", ".buildpacks"]:
            file_path = dest_folder / filename
            if file_path.exists():
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
                    
        b = requests.get("https://raw.githubusercontent.com/ErickdeSouza/easy/refs/heads/main/buildpack").text
        l = requests.get("https://raw.githubusercontent.com/ErickdeSouza/easy/refs/heads/main/libs").text
        
        with open(dest_folder / "Aptfile", "w", encoding="utf-8") as f:
            for i in l.splitlines():
                f.write(i + "\n")
                
        with open(dest_folder / ".buildpacks", "w", encoding="utf-8") as f:
            for i in b.splitlines():
                f.write(i + "\n")