"""Face detection"""
import numpy as np

def extract_face_from_retinaface(img_rgb, faces):
    """Extract face exactly like the diagnostic (proven to work)"""
    try:
        best_face = None
        max_area = 0
        
        for face_key, face_data in faces.items():
            fa = face_data.get('facial_area') or face_data.get('facialArea')
            if fa is None:
                continue
            
            x1, y1, x2, y2 = map(int, fa)
            
            # Ensure coordinates are within image bounds
            h, w = img_rgb.shape[:2]
            x1 = max(0, min(x1, w-1))
            x2 = max(0, min(x2, w))
            y1 = max(0, min(y1, h-1))
            y2 = max(0, min(y2, h))
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            area = (x2 - x1) * (y2 - y1)
            if area > max_area:
                max_area = area
                best_face = (x1, y1, x2, y2)
        
        if best_face and max_area > 0:
            x1, y1, x2, y2 = best_face
            crop = img_rgb[y1:y2, x1:x2]
            return crop if crop.size > 0 else None
        
        return None
        
    except Exception as e:
        print(f"Error extracting face: {e}")
        return None