# main.py
import cv2
import time
import detector
from collections import deque
from typing import Deque, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QImage, QColor
from config import *
from detector import ObjectDetector
from serial_communicate import SerialCommunicator
from shared import shared

number_counter = 0

class GarbageDetectionSystem(QObject):
    frame_ready = pyqtSignal(QImage)
    detection_result = pyqtSignal(list)
    status_changed = pyqtSignal(str)
    trigger_request = pyqtSignal()

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
        self.serial_timer = QTimer(self)
        self.serial_timer.moveToThread(self.thread())
        self.serial_timer.timeout.connect(self.check_serial)
        self.serial_timer.start(100)  # 每100ms检查一次串口

    def _init_camera(self):
        cap = cv2.VideoCapture(CAMERA_INDEX,cv2.CAP_DSHOW)
        if not cap.isOpened():
            for idx in [CAMERA_INDEX,0, 1, 2]:
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cap.isOpened():
                    print(f"成功通过自动探测打开摄像头索引 {idx}")
                    break
        return cap

    def check_serial(self):
        """检查串口消息"""
        if self.serial_com and self.serial_com.serial:
            try:
                if self.serial_com.serial.in_waiting > 0:
                    data = self.serial_com.serial.read(self.serial_com.serial.in_waiting).decode().strip()
                    print(f"接收到数据帧:{data}")
                    if "next" in data:
                        # self.start_detection_trigger()
                        self.trigger_request.emit()
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
        global number_counter
        try:
            retry_count = 0
            while self.running and retry_count <= 2:
                ret, frame = self.cap.read()
                if not ret:
                    print("摄像头读取失败, 尝试重新初始化...")
                    self.cap.release()
                    time.sleep(10)
                    self.cap = self._init_camera()
                    retry_count += 1
                    continue

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
                    print("time_outs = ",detector.time_outs)

                    if detected:
                       # print("detected:",detected)
                        current = detected[0]
                        #current_debug = detected[1]
                        current_pos = (current[2], current[3])
                        print("current = ",current)
                        self.position_history.append(current_pos)
                        
                       # print("time_outs = ",detector.time_outs)

                        if self.check_stability(current_pos):
                            trans_cx, trans_cy = self.detector.transform_coordinates(current[2], current[3])
                            #trans_cx_debug, trans_cy_debug = self.detector.transform_coordinates(current_debug[2], current_debug[3])
                            garbage_count = len(detected)

                            data_packet = f"{garbage_count}{current[1]+1}000{int(trans_cx):03d}{int(trans_cy):03d}"
                            #data_packet_debug = f"{garbage_count}{current_debug[1]+1}000{int(trans_cx_debug):03d}{int(trans_cy_debug):03d}"

                            try:
                                if self.serial_com:
                                    if DEBUG_MODE:
                                        number_counter += 1
                                        print("number_counter = ",number_counter)
                                        print(f"[串口调试] 已发送: {data_packet.strip()}")
                                        detector.time_outs = 0
                                        #print(f"[串口调试] 已发送: {data_packet_debug.strip()}")
                                    else:
                                        number_counter += 1
                                        self.serial_com.send_data(data_packet)
                                        detector.time_outs = 0
                                        
                            except Exception as e:
                                self.status_changed.emit(f"串口错误: {str(e)}")

                            shared.update_count.emit(current[1])
                            self.waiting_trigger = True
                            self.position_history.clear()
                            self.stable_count = 0

                        elif detector.time_outs >= TIMEOUT_THRESHOLD:
                            # 不稳定但是超时 强制发最后一个
                            trans_cx, trans_cy = self.detector.transform_coordinates(current[2], current[3])
                            #trans_cx_debug, trans_cy_debug = self.detector.transform_coordinates(current_debug[2], current_debug[3])
                            garbage_count = len(detected)

                            data_packet = f"{garbage_count}{current[1]+1}000{int(trans_cx):03d}{int(trans_cy):03d}"
                            #data_packet_debug = f"{garbage_count}{current_debug[1]+1}000{int(trans_cx_debug):03d}{int(trans_cy_debug):03d}"

                            try:
                                if self.serial_com:
                                    if DEBUG_MODE:
                                        number_counter += 1
                                        print("number_counter = ",number_counter)
                                        print(f"[TIMEOUT][串口调试] 已发送: {data_packet.strip()}")
                                        detector.time_outs = 0
                                        #print(f"[串口调试] 已发送: {data_packet_debug.strip()}")
                                    else:
                                        number_counter += 1
                                        self.serial_com.send_data(data_packet)
                                        detector.time_outs = 0
                                        
                            except Exception as e:
                                self.status_changed.emit(f"串口错误: {str(e)}")

                            shared.update_count.emit(current[1])
                            self.waiting_trigger = True
                            self.position_history.clear()
                            self.stable_count = 0

                    elif detector.time_outs >= TIMEOUT_THRESHOLD:
                        #持续啥也没有 直接发安全数据包
                        try:
                            if self.serial_com:
                                if DEBUG_MODE:
                                    number_counter += 1
                                    print("number_counter = ",number_counter)
                                    print(f"[TIMEOUT][串口调试][SAFETY] 已发送: {SAFETY_PACKET.strip()}")
                                    detector.time_outs = 0
                                    #print(f"[串口调试] 已发送: {data_packet_debug.strip()}")
                                else:
                                    number_counter += 1
                                    self.serial_com.send_data(SAFETY_PACKET)
                                    detector.time_outs = 0
                                        
                        except Exception as e:
                            self.status_changed.emit(f"串口错误: {str(e)}")

                        shared.update_count.emit(0)
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
        #global NUMBER_COUNTER
        #NUMBER_COUNTER += 1
        print(f"[Trigger] 触发信号来源: {'串口' if hasattr(self, 'keyboard') else '键盘'}") # 信号跟踪测试
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