import cv2
import serial

class ClassificationFunction:
    def __init__(self, serial_port="COM10", baud_rate=115200):
        """
        初始化垃圾分类系统，包括串口配置和结果列表。
        """
        self.ser = serial.Serial(serial_port, baud_rate, timeout=1)
        self.result_list = []  # 用于存储检测结果
        self.interval_sent = 0.5

    def create_test_data(self):
        """
        创建测试数据并存储到结果列表中。
        """
        from collections import namedtuple

        Result = namedtuple("Result", ["cls", "cx", "cy", "length", "width"])
        test_results = [
            Result(1, 67, 50, 50, 50),
            Result(3, 70, 45, 50, 50),
            Result(2, 55, 43, 50, 50),
            Result(0, 15, 20, 50, 50),
            Result(2, 25, 75, 50, 50)
        ]
        self.result_list.extend(test_results)
        print("Test data created and stored.")

    def take_photo(self, cap_number=1):
        """
        使用摄像头拍照并保存图片。
        """
        cap = cv2.VideoCapture(cap_number)
        if not cap.isOpened():
            print("无法打开摄像头")
            exit()
            
        # 设置裁剪范围（相对于原始图像的比例）
        x_range = (0.15, 0.75)  # 水平方向，从左边的15%到右边的75%
        y_range = (0.30, 0.80)   # 垂直方向，从上边的30%到下边的80%
        saved = 0

        while True:
            # 读取摄像头的一帧
            ret, frame = cap.read()
            if not ret:
                print("无法读取摄像头画面")
                break

            # 按自定义比例裁剪帧
            h, w, _ = frame.shape  # 获取原始帧的高和宽
    
            # 计算裁剪区域的边界
            x_start = int(w * x_range[0])
            x_end = int(w * x_range[1])
            y_start = int(h * y_range[0])
            y_end = int(h * y_range[1])

            # 确保范围合法
            x_start = max(0, x_start)
            x_end = min(w, x_end)
            y_start = max(0, y_start)
            y_end = min(h, y_end)

            # 裁剪帧
            cropped_frame = frame[y_start:y_end, x_start:x_end]

            # 调整裁剪后的图片大小为 640x480
            resized_frame = cv2.resize(cropped_frame, (640, 480),interpolation=cv2.INTER_LINEAR)

            cv2.imwrite("background.jpg", resized_frame)
            print("图片已保存为 background.jpg")
            saved += 1  # 更新标志变量，防止重复保存
            if saved == 10:
                break

        cap.release()
        cv2.destroyAllWindows()

    def send_introduction(self):
        """
        通过串口发送固定的初始化信息。
        """
        data_str = "5000000"
        self.ser.write(data_str.encode("utf-8"))
        print("We have sent the message:", data_str)

    def send_result_serial(self, cls, center_x, center_y):
        """
        将检测结果通过串口发送到下位机。
        """
        center_x = int(center_x)
        center_y = int(center_y)
        center_x = f"{center_x:03d}"
        center_y = f"{center_y:03d}"

        data_str = f"{cls}{center_x}{center_y}"
        self.ser.write(data_str.encode("utf-8"))
        print("We have sent the message:", data_str)
