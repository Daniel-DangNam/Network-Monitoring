from fastapi import APIRouter, Body
from typing import Optional, Dict, Any
from app.services.agent_service import agent_service

router = APIRouter()

@router.post("/start-agent")
def start_agent(payload: Optional[Dict[str, Any]] = Body(None)):
    duration = 30
    interface = None
    if payload:
        if "duration" in payload:
            try:
                duration = int(payload["duration"])
            except (ValueError, TypeError):
                duration = 30
        if "interface" in payload and payload["interface"]:
            interface = str(payload["interface"]).strip()
    return agent_service.start_agent(duration=duration, interface=interface)

@router.get("/network-interfaces")
def get_network_interfaces():
    return {
        "interfaces": agent_service.get_interfaces()
    }

@router.post("/stop-agent")
def stop_agent():
    return agent_service.stop_agent()

@router.get("/agent-status")
def get_agent_status():
    return agent_service.get_status()

@router.get("/agent-logs")
def get_agent_logs():
    return {
        "logs": agent_service.get_logs()
    }

