from pydantic import BaseModel
from typing import List, Optional

class PcapSummaryResponse(BaseModel):
    filename: str
    file_size_bytes: int
    total_packets: int
    total_flows: int = 0
    src_ip: str
    dst_ip: str
    protocol: str
    predicted_labels: List[str] = []
    error: Optional[str] = None

