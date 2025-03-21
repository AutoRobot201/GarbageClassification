"""
    @Author: WenXiaomo(SummerWen-Lab)
    @Date: 2025-03-22
    @Description: Configuration parameters for garbage detection system
"""

class Config:
    # Model path
    MODEL_PATH = "E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\Code\\garbage.pt"
    
    # Camera settings
    CAMERA_ID = 1
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    
    # Detection zone (x1,y1,x2,y2)
    DETECTION_ZONE = [200, 150, 440, 330]
    
    # Stability parameters
    STABLE_THRESHOLD = 8     # Consecutive stable frames required
    MOVE_THRESHOLD = 5.0     # Pixel movement threshold
    MATCH_DISTANCE = 30      # Object matching threshold
    
    # Frame rate control
    TARGET_FPS = 10
    FRAME_INTERVAL = 1.0 / TARGET_FPS
    
    # Display settings
    ZONE_COLOR = (0, 0, 255)
    ZONE_THICKNESS = 2
    TEXT_COLOR = (0, 255, 255)
    TEXT_SIZE = 0.6