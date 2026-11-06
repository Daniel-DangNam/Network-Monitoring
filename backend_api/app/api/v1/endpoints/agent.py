from fastapi import APIRouter
from app.services.agent_service import agent_service

router = APIRouter()

@router.post("/start-agent")
def start_agent():
    return agent_service.start_agent()

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

