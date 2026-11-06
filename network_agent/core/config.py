import os

class AgentConfig:
    # Backend Server
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/save-log")
    
    # Sniffing & Capture
    CAPTURE_INTERVAL: int = int(os.getenv("CAPTURE_INTERVAL", "10"))  # Seconds
    PACKET_LIMIT: int = int(os.getenv("PACKET_LIMIT", "500"))         # Max packets per interval
    NETWORK_INTERFACE: str = os.getenv("NETWORK_INTERFACE", "")       # Empty = default adapter
    
    # Storage Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "model_final_Application_Label.pth")
    if not os.path.exists(MODEL_PATH):
        MODEL_PATH = os.path.join(BASE_DIR, "model_final_Application_Label.pth")
        
    DATA_DIR = os.path.join(BASE_DIR, "data")
    CSV_DIR = os.path.join(DATA_DIR, "csv")
    PCAP_DIR = os.path.join(DATA_DIR, "pcaps")

config = AgentConfig()

