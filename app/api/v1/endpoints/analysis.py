from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.report import Report
from app.schemas import analysis as schemas
from app.services.ml_model import roof_model
from app.services.tf_model import tf_model
from app.services import image_processing, solar_calculator
import shutil
import os
import uuid
from PIL import Image
import numpy as np
import cv2

router = APIRouter()

UPLOAD_DIR = "app/data/uploads"
MASK_DIR = "app/data/masks"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MASK_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.ReportResponse)
async def upload_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    print(f"Received upload request: {file.filename}")
    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    print(f"Saving to: {file_path}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print("File saved successfully")
    report = Report(image_path=file_path, metadata_info={"original_filename": file.filename})
    db.add(report)
    await db.commit()
    await db.refresh(report)
    print(f"Report created with ID: {report.id}")
    return report

@router.post("/segment", response_model=schemas.ReportResponse)
async def segment_image(request: schemas.SegmentRequest, db: AsyncSession = Depends(get_db)):
    print(f"Segmenting report ID: {request.report_id}")
    report = await db.get(Report, request.report_id)
    if not report:
        print("Report not found")
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Load image
    try:
        print(f"Opening image: {report.image_path}")
        image = Image.open(report.image_path).convert("RGB")
    except Exception as e:
        print(f"Error opening image: {e}")
        raise HTTPException(status_code=500, detail=f"Could not open image: {str(e)}")

    # Run inference
    print("Running inference...")
    if request.model_type == "tensorflow":
        mask = tf_model.predict(image)
    else:
        mask = roof_model.predict(image)
    print("Inference complete")
    
    # Save mask
    mask_filename = f"mask_{os.path.basename(report.image_path)}.png"
    mask_path = os.path.join(MASK_DIR, mask_filename)
    
    # Convert mask to image and save
    # mask is likely class indices, we need to scale it up to be visible or just save as is
    # For binary mask (0 or 1), we multiply by 255
    mask_img = Image.fromarray((mask * 255).astype(np.uint8))
    mask_img.save(mask_path)
    
    report.mask_path = mask_path
    await db.commit()
    await db.refresh(report)
    return report

@router.post("/calculate", response_model=schemas.ReportResponse)
async def calculate_area(request: schemas.CalculateRequest, db: AsyncSession = Depends(get_db)):
    report = await db.get(Report, request.report_id)
    if not report or not report.mask_path:
        raise HTTPException(status_code=400, detail="Report or mask not found")
    
    mask = cv2.imread(report.mask_path, cv2.IMREAD_GRAYSCALE)
    # Count non-zero pixels
    pixel_count = cv2.countNonZero(mask)
    
    total_area = solar_calculator.calculate_area(pixel_count, request.scale_factor)
    # Assume 85% usable for now as per prompt requirement, or we could do more complex logic
    usable_area = total_area * 0.85 
    
    report.total_area = total_area
    report.usable_area = usable_area
    
    await db.commit()
    await db.refresh(report)
    return report

@router.post("/panel-estimation", response_model=schemas.ReportResponse)
async def estimate_panels(request: schemas.EstimationRequest, db: AsyncSession = Depends(get_db)):
    report = await db.get(Report, request.report_id)
    if not report or report.usable_area is None:
        raise HTTPException(status_code=400, detail="Report or usable area not found")
    
    panel_count = solar_calculator.estimate_panels(report.usable_area, request.panel_area)
    capacity = solar_calculator.estimate_capacity(panel_count, request.panel_wattage)
    
    report.panel_count = panel_count
    report.solar_capacity = capacity
    
    # --- Visualization Generation ---
    try:
        if report.image_path and report.mask_path:
            original = cv2.imread(report.image_path)
            mask = cv2.imread(report.mask_path, cv2.IMREAD_GRAYSCALE)
            
            # Simple assumption directly from pixel scale if known, or infer.
            # We don't have the exact pixel scale stored from calculate_area request unless we passed it.
            # But let's approximate based on usable_area and pixel count of mask.
            pixel_count = cv2.countNonZero(mask)
            if pixel_count > 0:
                # scale_factor = sqrt(total_area / pixel_count) -- Wait total_area = pixels * scale^2
                # So scale = sqrt(total_area / pixel_count)
                # But here we are in a separate request. Let's assume a default or recalculate if we had scale stored.
                # For this demo, let's assume 1 pixel ~ 0.1 meter (which was the default in calculate request)
                # Ideally, we should store scale_factor in the DB.
                
                # Let's define panel size in pixels
                # Panel 1.6m x 1.0m
                # If 1 px = 0.1m, then panel is 16px x 10px
                
                # Let's derive scale from stored total_area if available
                scale_factor = 0.1
                if report.total_area and pixel_count > 0:
                    scale_factor = (report.total_area / pixel_count) ** 0.5
                
                panel_w_px = int(1.0 / scale_factor)
                panel_h_px = int(1.6 / scale_factor)
                
                vis_image = image_processing.visualize_panels(original, mask, panel_w_px, panel_h_px)
                
                vis_filename = f"panels_{os.path.basename(report.image_path)}"
                vis_path = os.path.join(UPLOAD_DIR, vis_filename) # Save in uploads or new dir? Uploads is served static.
                cv2.imwrite(vis_path, vis_image)
                report.panel_layout_path = vis_path
    
    except Exception as e:
        print(f"Error generating visualization: {e}")
        # Don't fail the whole request just for visualization
    
    await db.commit()
    await db.refresh(report)
    return report

@router.get("/{id}", response_model=schemas.ReportResponse)
async def get_report(id: int, db: AsyncSession = Depends(get_db)):
    report = await db.get(Report, id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
