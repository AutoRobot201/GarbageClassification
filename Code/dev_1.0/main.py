"""
    @Author: WenXiaomo(SummerWen-Lab)
    @Date: 2025-03-22
    @Description: Main program entry for garbage detection system

    Garbage Classification:
    0 : Wrong Type
    1 : Recycle Waste
    2 : Kitchen Waste
    3 : Harmful Waste
    4 : Other Waste
"""

import cv2
from time import time
from config import Config
from detector import Detector
from tracker import ObjectTracker
from visualizer import Visualizer

class GarbageDetectionSystem:
    def __init__(self):
        """Initialize system components"""
        self.cap = cv2.VideoCapture(Config.CAMERA_ID)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
        
        self.detector = Detector()
        self.tracker = ObjectTracker()
        self.last_time = time()
        self.frame_count = 0
    
    def run(self):
        """Main execution loop"""
        try:
            while True:
                if not self._check_frame_rate():
                    continue
                
                frame = self._read_frame()
                if frame is None:
                    break
                
                detections = self._process_detection(frame)
                self._process_tracking(detections)
                self._visualize(frame)
                
                if self._check_exit():
                    break
        finally:
            self._cleanup()
    
    def _check_frame_rate(self):
        """Control frame processing rate"""
        current_time = time()
        if current_time - self.last_time < Config.FRAME_INTERVAL:
            return False
        self.last_time = current_time
        self.frame_count += 1
        return True
    
    def _read_frame(self):
        """Capture frame from camera"""
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame")
            return None
        return frame
    
    def _process_detection(self, frame):
        """Process object detection"""
        detections = self.detector.detect(frame)
        return [d for d in detections if self._in_detection_zone(d['pos'])]
    
    def _in_detection_zone(self, pos):
        """Check if position is within target zone"""
        x, y = pos
        x1, y1, x2, y2 = Config.DETECTION_ZONE
        return x1 <= x <= x2 and y1 <= y <= y2
    
    def _process_tracking(self, detections):
        """Process object tracking"""
        self.tracker.update(detections)
        for obj_id, obj in self.tracker.get_stable_objects():
            self._handle_stable_object(obj_id, obj)
    
    def _handle_stable_object(self, obj_id, obj):
        """Handle stable object detection"""
        last_pos = obj['positions'][-1]
        trans_x = (last_pos[1] - 110) * 0.61884 + 50
        trans_y = (last_pos[0] - 190) * 0.61884 + 10
        print(  
            f"\n🚀 Stable Object {obj_id} | "
            f"Class: {obj['class']} | "
            # f"Position: ({last_pos[0]:.1f}, {last_pos[1]:.1f}) | "
            f"Position_trans: ({trans_x:.0f}, {trans_y:.0f}) | "
            f"Confidence: {obj['confidence']:.2f}"
        )
    
    def _visualize(self, frame):
        """Handle visualization"""
        Visualizer.draw_detection_zone(frame)
        Visualizer.draw_tracking_info(frame, self.tracker.tracked_objects)
        Visualizer.show_frame(frame)
    
    def _check_exit(self):
        """Check exit condition"""
        return cv2.waitKey(1) & 0xFF == ord('q')
    
    def _cleanup(self):
        """Release resources"""
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    system = GarbageDetectionSystem()
    system.run()