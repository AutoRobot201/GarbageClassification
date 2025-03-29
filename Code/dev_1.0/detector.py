"""
    @Author: WenXiaomo(SummerWen-Lab)
    @Date: 2025-03-22
    @Description: Object detection module using YOLOv11
"""

from ultralytics import YOLO
from config import Config

class Detector:
    def __init__(self):
        """Initialize YOLO model"""
        self.model = YOLO(Config.MODEL_PATH)
    
    def detect(self, frame):
        """Perform object detection on input frame
        Args:
            frame: Input image frame
        Returns:
            List of detections with positions and class info
        """
        results = self.model(frame, verbose=False)
        return self._parse_results(results)
    
    def _parse_results(self, results):
        """Parse YOLO detection results
        Args:
            results: Raw YOLO detection results
        Returns:
            List of processed detections
        """
        detections = []
        for result in results:
            for box in result.boxes:
                x_center, y_center = map(float, box.xywh[0][:2])
                detections.append({
                    'pos': (x_center, y_center),
                    'class': int(box.cls[0]),
                    'confidence': float(box.conf[0])
                })
        return detections