from ultralytics import YOLO
import cv2
from typing import List, Tuple

class ObjectDetector:
    def __init__(self, model_path: str, detection_zone: list, coord_config: dict):
        self.model = YOLO(model_path)
        self.detection_zone = detection_zone
        self.x_offset = coord_config['x_offset']
        self.y_offset = coord_config['y_offset']
        self.x_scale = coord_config['x_scale']
        self.y_scale = coord_config['y_scale']
        self.result_offset = coord_config['result_offset']

    def transform_coordinates(self, cx: int, cy: int) -> Tuple[int, int]:
        """执行坐标转换"""
        trans_cx = int((cy + self.y_offset) * self.y_scale + self.result_offset[0])
        trans_cy = int((cx + self.x_offset) * self.x_scale + self.result_offset[1])
        return trans_cx, trans_cy

    def process_frame(self, frame) -> List[Tuple]:
        """处理单帧检测"""
        CONF_THRESHOLD = 0.7
        x1, y1, x2, y2 = self.detection_zone
        roi = frame[y1:y2, x1:x2]
        results = self.model(roi)
        
        detected = []
        for result in results:
            for box, cls, conf in zip(result.boxes.xyxy.cpu().numpy(),
                                     result.boxes.cls.cpu().numpy().astype(int),
                                     result.boxes.conf.cpu().numpy()):
                if conf < CONF_THRESHOLD: continue
                
                if cls == 2 or cls == 3 or cls == 9 : cls = 0
                elif cls == 0 or cls == 1 : cls = 1
                elif cls == 4 or cls == 5 or cls == 6 : cls = 2
                elif cls == 7 or cls == 8 : cls = 3

                if 0 <= cls <= 4:
                    x_min, y_min, x_max, y_max = map(int, box)
                    global_x_min = x_min + x1
                    global_y_min = y_min + y1
                    global_x_max = x_max + x1
                    global_y_max = y_max + y1
                    
                    area = (x_max - x_min) * (y_max - y_min)
                    cx = (global_x_min + global_x_max) // 2 
                    cy = (global_y_min + global_y_max) // 2 
                    
                    detected.append((
                        area, cls, cx + 10, cy + 5,
                        global_x_min, global_y_min,
                        global_x_max, global_y_max
                    ))
        
        return sorted(detected, key=lambda x: x[0], reverse=True)