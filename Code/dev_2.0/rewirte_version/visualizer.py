import cv2
from typing import List, Tuple

class Visualizer:
    def __init__(self, detection_zone: list, visual_config: dict):
        self.detection_zone = detection_zone
        self.box_color = visual_config['box_color']
        self.center_color = visual_config['center_color']
        self.text_color = visual_config['text_color']
        self.box_thickness = visual_config['box_thickness']
        self.center_radius = visual_config['center_radius']

    def draw_elements(self, frame, detected: List[Tuple], status_text: str):
        """绘制可视化元素"""
        # 绘制检测区域
        x1, y1, x2, y2 = self.detection_zone
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 绘制检测结果
        if detected:
            for obj in detected:
                _, cls, cx, cy, x1_, y1_, x2_, y2_ = obj     
                cv2.rectangle(frame, (x1_, y1_), (x2_, y2_), 
                            self.box_color, self.box_thickness)
                cv2.circle(frame, (cx, cy), self.center_radius,
                          self.center_color, -1)
                cv2.putText(frame, f"Class:{cls}", (x1_+5, y1_+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                           self.text_color, 2)
        
        # 状态显示
        cv2.putText(frame, status_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame