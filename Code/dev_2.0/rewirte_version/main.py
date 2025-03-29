import cv2
from typing import Deque, Tuple
from collections import deque
from config import *
from detector import ObjectDetector
from visualizer import Visualizer
from serial_communicate import SerialCommunicator

class GarbageDetectionSystem:
    def __init__(self):
        # 初始化模块
        self.serial_com = SerialCommunicator(SERIAL_PORT, BAUDRATE)
        self.detector = ObjectDetector(MODEL_PATH, DETECTION_ZONE, COORD_TRANSFORM)
        self.visualizer = Visualizer(DETECTION_ZONE, VISUAL_CONFIG)
        
        # 初始化摄像头
        self.cap = self._init_camera()
        
        # 状态控制
        self.waiting_trigger = True
        self.stable_count = 0
        self.position_history: Deque[Tuple[int, int]] = deque(maxlen=STABILITY_FRAMES)

    def _init_camera(self):
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            raise RuntimeError("无法打开摄像头")
        return cap

    def check_stability(self, current_pos: Tuple[int, int]) -> bool:
        if len(self.position_history) < STABILITY_FRAMES:
            return False
        return all(
            abs(current_pos[0] - pos[0]) < STABILITY_THRESHOLD and
            abs(current_pos[1] - pos[1]) < STABILITY_THRESHOLD
            for pos in self.position_history
        )

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("视频流中断")
                    break
                
                key = cv2.waitKey(1)
                if key == 13:  # Enter键
                    self.waiting_trigger = False
                elif key == ord('q'):
                    break
                
                detected = []
                if not self.waiting_trigger:
                    detected = self.detector.process_frame(frame)
                    
                    if detected:
                        current = detected[0]
                        current_pos = (current[2], current[3])
                        self.position_history.append(current_pos)
                        
                        if self.check_stability(current_pos):
                            trans_cx, trans_cy = self.detector.transform_coordinates(*current_pos)
                            data_frame = f"{len(detected)}{current[1]}000{trans_cx:03d}{trans_cy:03d}"
                            
                            print(f"[稳定检测] 类别:{current[1]} 坐标({trans_cx},{trans_cy}) 数据帧: {data_frame}")
                            self.serial_com.send_data(data_frame) # 这里通过串口向下位机发送数据
                            
                            self.waiting_trigger = True
                            self.position_history.clear()
                            self.stable_count = 0
                        else:
                            self.stable_count = min(self.stable_count+1, STABILITY_FRAMES)
                    else:
                        self.position_history.clear()
                        self.stable_count = 0
                
                # 更新界面
                status_text = ("Awaiting Trigger" if self.waiting_trigger 
                              else f"Stabilization {self.stable_count}/{STABILITY_FRAMES}")
                cv2.imshow('Garbage Detection', 
                          self.visualizer.draw_elements(frame, detected, status_text))
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.serial_com.close()

if __name__ == "__main__":
    try:
        print("=== 垃圾分类检测系统启动 ===")
        system = GarbageDetectionSystem()
        system.run()
        print("=== 系统正常退出 ===")
    except Exception as e:
        print(f"!! 系统异常: {str(e)}")