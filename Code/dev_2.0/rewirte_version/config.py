# 系统配置参数
MODEL_PATH = 'E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\Code\\dev_2.0\\models\\small_base\\best-mix-yolov8s_ep100_batch16.pt'
SERIAL_PORT = 'COM6'
BAUDRATE = 115200
CAMERA_INDEX = 0
DETECTION_ZONE = [182,120,450,382]
STABILITY_THRESHOLD = 3
STABILITY_FRAMES = 4
DEBUG_MODE = True
HISTORY_FRAMES = 5

TIMEOUT_THRESHOLD = 15
SAFETY_PACKET = "11000000000"

# 坐标转换参数
COORD_TRANSFORM = {
    'x_offset': -182,
    'y_offset': -120,
    'x_scale': 0.57252,
    'y_scale': 0.57252,
    'result_offset': (50, 10)
}

# 可视化参数
VISUAL_CONFIG = {
    'box_color': (0, 0, 255),
    'center_color': (255, 0, 255),
    'text_color': (255, 255, 0),
    'box_thickness': 2,
    'center_radius': 3
}