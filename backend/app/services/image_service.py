import cv2
import numpy as np
from typing import List, Optional
from PIL import Image
import io


class ImageService:
    def __init__(self):
        pass

    def preprocess_image(self, image_data: bytes) -> bytes:
        """Preprocess image using OpenCV for better recognition"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return image_data
            
            # Enhance image quality
            # Convert to RGB (OpenCV uses BGR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Apply slight sharpening
            kernel = np.array([[-1, -1, -1],
                              [-1, 9, -1],
                              [-1, -1, -1]])
            sharpened = cv2.filter2D(img_rgb, -1, kernel)
            
            # Enhance contrast
            lab = cv2.cvtColor(sharpened, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
            
            # Convert back to bytes
            pil_image = Image.fromarray(enhanced_rgb)
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=90)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return image_data

    def validate_image(self, image_data: bytes) -> bool:
        """Validate that the uploaded file is a valid image"""
        try:
            img = Image.open(io.BytesIO(image_data))
            img.verify()
            return True
        except Exception:
            return False

