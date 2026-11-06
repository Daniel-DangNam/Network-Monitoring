import subprocess
import os
import sys
import signal
import platform
from app.core.config import settings

class AgentService:
    def __init__(self):
        self._process = None

    def is_running(self) -> bool:
        if self._process is not None and self._process.poll() is None:
            return True
        
        # Trên môi trường Linux/Ubuntu: Kiểm tra thêm tiến trình chạy độc lập qua pgrep
        if platform.system() != "Windows":
            try:
                res = subprocess.run(
                    ["pgrep", "-f", "live_pipeline.py"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
                if res.returncode == 0 and res.stdout.strip():
                    return True
            except Exception:
                pass

        return False

    def get_status(self) -> dict:
        running = self.is_running()
        iface = os.getenv("NETWORK_INTERFACE", "auto (eth0/ens33)").strip()
        if not iface:
            iface = "auto (eth0/ens33)"
        return {
            "is_running": running,
            "pid": self._process.pid if (self._process and self._process.poll() is None) else None,
            "interface": iface
        }

    def start_agent(self) -> dict:
        if self.is_running():
            return {"status": "info", "message": "Network Agent đang chạy rồi!"}

        # Tự động xác định đường dẫn Python và script (hỗ trợ venv trên Ubuntu/Linux và Windows)
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        agent_dir = os.path.join(os.path.dirname(current_dir), "network_agent")
        
        if not settings.AGENT_PYTHON_EXEC:
            candidate_venvs = [
                os.path.join(agent_dir, "venv", "bin", "python"),
                os.path.join(os.path.dirname(current_dir), "venv", "bin", "python"),
                os.path.join(current_dir, "venv", "bin", "python"),
                os.path.join(agent_dir, "venv", "Scripts", "python.exe"),
                os.path.join(os.path.dirname(current_dir), "venv", "Scripts", "python.exe"),
                os.path.join(current_dir, "venv", "Scripts", "python.exe"),
            ]
            if platform.system() != "Windows" and os.path.exists("/usr/bin/python3"):
                candidate_venvs.append("/usr/bin/python3")

            python_exec = sys.executable
            for cand in candidate_venvs:
                if os.path.exists(cand):
                    python_exec = cand
                    break
        else:
            python_exec = settings.AGENT_PYTHON_EXEC
        
        script_path = settings.AGENT_SCRIPT_PATH or os.path.join(agent_dir, "live_pipeline.py")

        if not os.path.exists(script_path):
            script_path = os.path.join(agent_dir, "main.py")

        try:
            kwargs = {}
            if platform.system() != "Windows":
                kwargs["preexec_fn"] = os.setsid
            else:
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

            env = os.environ.copy()
            if not env.get("NETWORK_INTERFACE"):
                env["NETWORK_INTERFACE"] = ""

            log_file = open(os.path.join(agent_dir, "agent.log"), "w", encoding="utf-8")
            self._process = subprocess.Popen(
                [python_exec, "-u", script_path],
                cwd=agent_dir if os.path.exists(agent_dir) else None,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                env=env,
                **kwargs
            )
            return {"status": "success", "message": "Đã khởi động AI Network Agent thành công!"}
        except Exception as e:
            return {"status": "error", "message": f"Lỗi khi khởi động Agent: {str(e)}"}

    def stop_agent(self) -> dict:
        if not self.is_running():
            return {"status": "info", "message": "Network Agent hiện không chạy."}

        try:
            if self._process is not None and self._process.poll() is None:
                if platform.system() != "Windows":
                    try:
                        os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
                    except Exception:
                        self._process.terminate()
                else:
                    self._process.terminate()
            self._process = None

            # Trên Linux: đảm bảo quét sạch mọi tiến trình con của live_pipeline nếu có
            if platform.system() != "Windows":
                try:
                    subprocess.run(["pkill", "-f", "live_pipeline.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass

            return {"status": "success", "message": "Đã dừng AI Network Agent an toàn!"}
        except Exception as e:
            return {"status": "error", "message": f"Lỗi khi dừng Agent: {str(e)}"}

agent_service = AgentService()


