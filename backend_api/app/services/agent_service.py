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
        return self._process is not None and self._process.poll() is None

    def start_agent(self) -> dict:
        if self.is_running():
            return {"status": "info", "message": "Network Agent đang chạy rồi!"}

        # Tự động xác định đường dẫn Python và script
        python_exec = settings.AGENT_PYTHON_EXEC or sys.executable
        
        # Tìm đường dẫn đến live_pipeline.py hoặc main.py của network_agent
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        agent_dir = os.path.join(os.path.dirname(current_dir), "network_agent")
        script_path = settings.AGENT_SCRIPT_PATH or os.path.join(agent_dir, "live_pipeline.py")

        if not os.path.exists(script_path):
            script_path = os.path.join(agent_dir, "main.py")

        try:
            kwargs = {}
            if platform.system() != "Windows":
                kwargs["preexec_fn"] = os.setsid
            else:
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

            log_file = open(os.path.join(agent_dir, "agent.log"), "w", encoding="utf-8")
            self._process = subprocess.Popen(
                [python_exec, "-u", script_path],
                cwd=agent_dir if os.path.exists(agent_dir) else None,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                **kwargs
            )
            return {"status": "success", "message": "Đã khởi động AI Network Agent thành công!"}
        except Exception as e:
            return {"status": "error", "message": f"Lỗi khi khởi động Agent: {str(e)}"}

    def stop_agent(self) -> dict:
        if not self.is_running():
            return {"status": "info", "message": "Network Agent hiện không chạy."}

        try:
            if platform.system() != "Windows":
                os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            else:
                self._process.terminate()
            self._process = None
            return {"status": "success", "message": "Đã dừng AI Network Agent an toàn!"}
        except Exception as e:
            return {"status": "error", "message": f"Lỗi khi dừng Agent: {str(e)}"}

agent_service = AgentService()

