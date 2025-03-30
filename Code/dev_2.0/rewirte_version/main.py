# main.py
import cv2
import time
from collections import deque
from typing import Deque, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QImage, QColor
from config import *
from detector import ObjectDetector
from serial_communicate import SerialCommunicator
from shared import shared

class GarbageDetectionSystem(QObject):
    frame_ready = pyqtSignal(QImage)
    detection_result = pyqtSignal(list)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.serial_com = SerialCommunicator(SERIAL_PORT, BAUDRATE)
        self.detector = ObjectDetector(MODEL_PATH, DETECTION_ZONE, COORD_TRANSFORM)
        self.cap = self._init_camera()
        self.running = True
        self.waiting_trigger = True
        self.stable_count = 0
        self.position_history: Deque[Tuple[int, int]] = deque(maxlen=STABILITY_FRAMES)
        self.last_serial_check = time.time()
        
        # 串口检测定时器
        self.serial_timer = QTimer()
        self.serial_timer.timeout.connect(self.check_serial)
        self.serial_timer.start(100)  # 每100ms检查一次串口

    def _init_camera(self):
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            raise RuntimeError("无法打开摄像头")
        return cap

    def check_serial(self):
        """检查串口消息"""
        if self.serial_com and self.serial_com.serial:
            try:
                if self.serial_com.serial.in_waiting > 0:
                    data = self.serial_com.serial.read(self.serial_com.serial.in_waiting).decode().strip()
                    if "next" in data:
                        self.start_detection_trigger()
            except Exception as e:
                print(f"串口读取错误: {str(e)}")

    def check_stability(self, current_pos: Tuple[int, int]) -> bool:
        if len(self.position_history) < STABILITY_FRAMES:
            return False
        return all(
            abs(current_pos[0] - pos[0]) < STABILITY_THRESHOLD and
            abs(current_pos[1] - pos[1]) < STABILITY_THRESHOLD
            for pos in self.position_history
        )

    def start_detection(self):
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret: break

                # 绘制ROI区域
                x1, y1, x2, y2 = DETECTION_ZONE
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 处理检测逻辑
                processed_frame = self.process_frame(frame.copy())
                self._emit_frame(processed_frame)
                
                detected = []
                if not self.waiting_trigger:
                    detected = self.detector.process_frame(frame)
                    self.detection_result.emit(detected)
                    
                    if detected:
                        current = detected[0]
                        current_pos = (current[2], current[3])
                        self.position_history.append(current_pos)
                        
                        if self.check_stability(current_pos):
                            shared.update_count.emit(current[1])
                            self.waiting_trigger = True
                            self.position_history.clear()
                            self.stable_count = 0

                self._update_status()

        finally:
            self.stop()

    def process_frame(self, frame):
        """绘制检测结果"""
        if not self.waiting_trigger:
            # 绘制历史轨迹
            for pos in self.position_history:
                cv2.circle(frame, pos, 3, (255, 0, 255), -1)
        return frame

    def _emit_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.frame_ready.emit(qt_image)

    def _update_status(self):
        status = "等待触发 ▶ 按Enter键或发送'next'指令开始检测" if self.waiting_trigger else \
                f"检测中... 稳定进度: {self.stable_count}/{STABILITY_FRAMES}"
        self.status_changed.emit(status)

    def start_detection_trigger(self):
        self.waiting_trigger = False
        self.stable_count = 0
        self.position_history.clear()

    def stop(self):
        self.running = False
        self.serial_timer.stop()
        self.cap.release()
        cv2.destroyAllWindows()
        self.serial_com.close()
        shared.system_stop.emit()