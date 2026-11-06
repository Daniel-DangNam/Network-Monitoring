import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.pcap import PcapSummaryResponse
from app.services.pcap_service import pcap_service

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=PcapSummaryResponse)
async def upload_pcap(file: UploadFile = File(...)):
    if not file.filename.endswith((".pcap", ".pcapng", ".cap")):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp định dạng .pcap hoặc .pcapng!")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = pcap_service.parse_pcap_file(file_path)
        result["filename"] = file.filename
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý file PCAP: {str(e)}")

