import cv2
import serial
from typing import Optional, List, Tuple, Deque
from collections import deque
from ultralytics import YOLO

class GarbageDetectionSystem:
    """垃圾分类检测系统（完整重构版）"""
    
    def __init__(self, config: dict):
        # 硬件参数
        self.serial_port = config['serial_port']
        self.baudrate = config['baudrate']
        self.camera_index = config['camera_index']
        self.model_path = config['model_path']
        
        # 检测参数
        self.detection_zone = config['detection_zone']
        self.stability_threshold = config.get('stability_threshold', 20)
        self.stability_frames = config.get('stability_frames', 15)
        
        # 可视化参数
        self.box_color = config.get('box_color', (0, 0, 255))
        self.center_color = config.get('center_color', (255, 0, 255))
        self.text_color = config.get('text_color', (255, 255, 0))
        self.box_thickness = config.get('box_thickness', 2)
        self.center_radius = config.get('center_radius', 5)
        
        # 坐标转换参数
        coord_config = config.get('coord_transform', {
            'x_offset': -190,
            'y_offset': -110,
            'x_scale': 0.61884,
            'y_scale': 0.61884,
            'result_offset': (50, 10)
        })
        self.x_offset = coord_config['x_offset']
        self.y_offset = coord_config['y_offset']
        self.x_scale = coord_config['x_scale']
        self.y_scale = coord_config['y_scale']
        self.result_offset = coord_config['result_offset']
        
        # 初始化组件
        self.serial = self._init_serial()
        self.cap = self._init_camera()
        self.model = YOLO(self.model_path)
        
        # 状态控制
        self.waiting_trigger = True
        self.stable_count = 0
        self.position_history: Deque[Tuple[int, int]] = deque(maxlen=self.stability_frames)

    def _init_serial(self) -> Optional[serial.Serial]:
        """初始化串口连接"""
        try:
            ser = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=0.1
            )
            print(f"成功打开串口 {self.serial_port}")
            return ser
        except Exception as e:
            print(f"串口连接失败: {str(e)}")
            return None

    def _init_camera(self) -> cv2.VideoCapture:
        """初始化摄像头"""
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError("无法打开摄像头")
        return cap

    def transform_coordinates(self, cx: int, cy: int) -> Tuple[int, int]:
        """执行坐标转换"""
        trans_cx = int((cy + self.y_offset) * self.y_scale + self.result_offset[0])
        trans_cy = int((cx + self.x_offset) * self.x_scale + self.result_offset[1])
        return trans_cx, trans_cy

    def check_stability(self, current_pos: Tuple[int, int]) -> bool:
        """检查位置稳定性"""
        if len(self.position_history) < self.stability_frames:
            return False
        return all(
            abs(current_pos[0] - pos[0]) < self.stability_threshold and
            abs(current_pos[1] - pos[1]) < self.stability_threshold
            for pos in self.position_history
        )

    def process_frame(self, frame) -> List[Tuple]:
        """处理单帧检测"""
        x1, y1, x2, y2 = self.detection_zone
        roi = frame[y1:y2, x1:x2]
        results = self.model(roi)
        
        detected = []
        for result in results:
            for box, cls, conf in zip(result.boxes.xyxy.cpu().numpy(),
                                     result.boxes.cls.cpu().numpy().astype(int),
                                     result.boxes.conf.cpu().numpy()):
                if 0 <= cls <= 4:
                    x_min, y_min, x_max, y_max = map(int, box)
                    # 转换为全局坐标
                    global_x_min = x_min + x1
                    global_y_min = y_min + y1
                    global_x_max = x_max + x1
                    global_y_max = y_max + y1
                    
                    # 计算特征值
                    area = (x_max - x_min) * (y_max - y_min)
                    cx = (global_x_min + global_x_max) // 2
                    cy = (global_y_min + global_y_max) // 2
                    
                    detected.append((
                        area, cls, cx, cy,
                        global_x_min, global_y_min,
                        global_x_max, global_y_max
                    ))
        
        return sorted(detected, key=lambda x: x[0], reverse=True)

    def draw_visualization(self, frame, detected: List[Tuple]):
        """绘制可视化元素"""
        # 绘制检测区域
        x1, y1, x2, y2 = self.detection_zone
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 绘制检测结果
        if detected:
            for obj in detected:
                _, cls, cx, cy, x1_, y1_, x2_, y2_ = obj
                
                # 边界框
                cv2.rectangle(frame, (x1_, y1_), (x2_, y2_), 
                            self.box_color, self.box_thickness)
                # 中心点
                cv2.circle(frame, (cx, cy), self.center_radius,
                          self.center_color, -1)
                # 类别标签
                cv2.putText(frame, f"Class:{cls}", (x1_+5, y1_+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                           self.text_color, 2)
        
        # 状态显示
        status_text = ("Awaiting Trigger" if self.waiting_trigger 
                      else f"Stabilization {self.stable_count}/{self.stability_frames}")
        cv2.putText(frame, status_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame

    def send_data_frame(self, data: str):
        """发送数据帧"""
        print(f"稳定数据帧: {data}")
        if self.serial:
            try:
                self.serial.write(data.encode())
            except Exception as e:
                print(f"串口发送失败: {str(e)}")

    def run(self):
        """主运行循环"""
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("视频流中断")
                    break
                
                # 处理用户输入
                key = cv2.waitKey(1)
                if key == 13:  # Enter键
                    self.waiting_trigger = False
                elif key == ord('q'):
                    break
                
                # 处理串口指令
                if self.serial and self.serial.in_waiting > 0:
                    try:
                        if "next" in self.serial.read(self.serial.in_waiting).decode().strip():
                            self.waiting_trigger = False
                    except UnicodeDecodeError:
                        pass
                
                # 检测流程
                detected = []
                if not self.waiting_trigger:
                    detected = self.process_frame(frame)
                    
                    if detected:
                        current = detected[0]
                        current_pos = (current[2], current[3])
                        self.position_history.append(current_pos)
                        
                        if self.check_stability(current_pos):
                            # 生成并发送数据
                            trans_cx, trans_cy = self.transform_coordinates(*current_pos)
                            data_frame = (f"{len(detected)}{current[1]}000"
                                         f"{trans_cx:03d}{trans_cy:03d}")
                            self.send_data_frame(data_frame)
                            
                            # 重置状态
                            self.waiting_trigger = True
                            self.position_history.clear()
                            self.stable_count = 0
                        else:
                            self.stable_count = min(self.stable_count+1, self.stability_frames)
                    else:
                        self.position_history.clear()
                        self.stable_count = 0
                
                # 更新界面
                cv2.imshow('Garbage Detection', self.draw_visualization(frame, detected))
        
        finally:
            # 释放资源
            self.cap.release()
            cv2.destroyAllWindows()
            if self.serial:
                self.serial.close()

if __name__ == "__main__":
    # ================= 系统配置 =================
    config = {
        'model_path': 'E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\Code\\dev_2.0\\garbage.pt',
        'serial_port': 'COM5',
        'baudrate': 115200,
        'camera_index': 1,  # 摄像头索引（0-默认摄像头，1-外接摄像头）
        'detection_zone': [190, 110, 445, 365],  # 检测区域[x1,y1,x2,y2]
        'stability_threshold': 15,  # 稳定检测阈值（像素）
        'stability_frames': 10,     # 需要连续稳定的帧数
        'coord_transform': {        # 坐标转换参数
            'x_offset': -190,
            'y_offset': -110,
            'x_scale': 0.61884,
            'y_scale': 0.61884,
            'result_offset': (50, 10)
        },
        # 可选可视化参数（不设置则使用默认值）
        # 'box_color': (0, 255, 0),  # BGR颜色
        # 'center_color': (0, 255, 255),
        # 'text_color': (0, 0, 255),
        # 'box_thickness': 3,
        # 'center_radius': 7
    }
    
    # ================= 启动系统 =================
    try:
        print("=== 垃圾分类检测系统启动 ===")
        system = GarbageDetectionSystem(config)
        system.run()
        print("=== 系统正常退出 ===")
    except Exception as e:
        print(f"!! 系统异常: {str(e)}")