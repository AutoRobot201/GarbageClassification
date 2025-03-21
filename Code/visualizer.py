"""
    @Author: WenXiaomo(SummerWen-Lab)
    @Date: 2025-03-22
    @Description: Visualization module for display output
"""

import cv2
from config import Config

class Visualizer:
    @staticmethod
    def draw_detection_zone(frame):
        """Draw detection zone rectangle
        Args:
            frame: Input/output image frame
        """
        cv2.rectangle(
            frame,
            (Config.DETECTION_ZONE[0], Config.DETECTION_ZONE[1]),
            (Config.DETECTION_ZONE[2], Config.DETECTION_ZONE[3]),
            Config.ZONE_COLOR,
            Config.ZONE_THICKNESS
        )
    
    @staticmethod
    def draw_tracking_info(frame, tracked_objects):
        """Draw object tracking information
        Args:
            frame: Input/output image frame
            tracked_objects: Dictionary of tracked objects
        """
        for obj_id, obj in tracked_objects.items():
            x, y = map(int, obj['positions'][-1])
            cv2.putText(
                frame,
                f"ID:{obj_id} S:{obj['stable_count']}",
                (x-20, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                Config.TEXT_SIZE,
                Config.TEXT_COLOR,
                2
            )
    
    @staticmethod
    def show_frame(frame):
        """Display output frame
        Args:
            frame: Image frame to display
        """
        cv2.imshow("Garbage Detection", frame)