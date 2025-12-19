import torch
from torchvision import models, transforms
from PIL import Image
import numpy as np

class RoofSegmentationModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.segmentation.deeplabv3_resnet50(pretrained=True)
        self.model.eval()
        self.model.to(self.device)
        self.preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def predict(self, image: Image.Image) -> np.ndarray:
        # Convert PIL Image to OpenCV format
        open_cv_image = np.array(image) 
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        
        from .image_processing import segment_roof_heuristic
        return segment_roof_heuristic(open_cv_image)

roof_model = RoofSegmentationModel()
