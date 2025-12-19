from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    mask_path = Column(String, nullable=True)
    total_area = Column(Float, nullable=True)
    usable_area = Column(Float, nullable=True)
    panel_count = Column(Integer, nullable=True)
    solar_capacity = Column(Float, nullable=True)
    panel_layout_path = Column(String, nullable=True)
    metadata_info = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
