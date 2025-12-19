from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ReportBase(BaseModel):
    image_path: str
    mask_path: Optional[str] = None
    total_area: Optional[float] = None
    usable_area: Optional[float] = None
    panel_count: Optional[int] = None
    solar_capacity: Optional[float] = None
    panel_layout_path: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SegmentRequest(BaseModel):
    report_id: int
    model_type: str = "pytorch" # or tensorflow

class CalculateRequest(BaseModel):
    report_id: int
    scale_factor: float = 0.1 # meters per pixel default

class EstimationRequest(BaseModel):
    report_id: int
    panel_area: float = 1.6
    panel_wattage: float = 400
