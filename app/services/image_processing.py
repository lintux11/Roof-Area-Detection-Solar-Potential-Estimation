import cv2
import numpy as np
from PIL import Image
import io

def process_image(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def denoise_image(image: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

def enhance_contrast(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

def get_contours(mask: np.ndarray):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def create_overlay(original: np.ndarray, mask: np.ndarray, color=(0, 255, 0), alpha=0.5) -> np.ndarray:
    mask_rgb = np.zeros_like(original)
    mask_rgb[mask > 0] = color
    return cv2.addWeighted(original, 1, mask_rgb, alpha, 0)

def segment_roof_heuristic(image: np.ndarray) -> np.ndarray:
    """
    Segment roof-like structures using heuristic computer vision techniques.
    Assumes roofs have distinct edges and contrast compared to surroundings.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge Detection (Canny)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Dilate edges to close gaps
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create empty mask
    mask = np.zeros_like(gray)
    
    # Filter contours based on area (assume roof is a significant part of the image)
    total_area = image.shape[0] * image.shape[1]
    min_area = total_area * 0.05  # At least 5% of the image
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            # Convex hull to get a cleaner shape
            hull = cv2.convexHull(contour)
            cv2.drawContours(mask, [hull], -1, (255), thickness=cv2.FILLED)
            
    # Morphological Close to fill holes
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    
    return mask

def visualize_panels(original: np.ndarray, mask: np.ndarray, panel_width_px: int, panel_height_px: int) -> np.ndarray:
    """
    Draw logical solar panel placement on the roof.
    """
    visualization = original.copy()
    overlay = original.copy()
    
    # Get bounding box of the mask
    y_indices, x_indices = np.where(mask > 0)
    if len(y_indices) == 0:
        return visualization
        
    y_min, y_max = np.min(y_indices), np.max(y_indices)
    x_min, x_max = np.min(x_indices), np.max(x_indices)
    
    # Simple grid based placement
    # In a real app, we would rotate the grid to align with the roof orientation.
    # Here we just iterate in a grid within the bounding box.
    
    panels_drawn = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    for y in range(y_min, y_max, panel_height_px + 2): # +2 for spacing
        for x in range(x_min, x_max, panel_width_px + 2):
            # Check if this rectangle is mostly inside the mask
            # We sample the center point or corners
            # Let's check center point
            cy = y + panel_height_px // 2
            cx = x + panel_width_px // 2
            
            if 0 <= cy < mask.shape[0] and 0 <= cx < mask.shape[1]:
                if mask[cy, cx] > 0:
                    # Draw panel
                    cv2.rectangle(overlay, (x, y), (x + panel_width_px, y + panel_height_px), (0, 0, 255), -1) # Blue filled
                    cv2.rectangle(overlay, (x, y), (x + panel_width_px, y + panel_height_px), (255, 255, 255), 1) # White border
                    panels_drawn += 1
                    
    # Blend overlay with original
    cv2.addWeighted(overlay, 0.4, visualization, 0.6, 0, visualization)
    
    # Add count text
    cv2.putText(visualization, f"Panels: {panels_drawn}", (30, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    
    return visualization
