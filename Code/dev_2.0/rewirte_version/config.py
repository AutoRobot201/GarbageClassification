# 系统配置参数
MODEL_PATH = 'E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\Code\\dev_2.0\\models\\middle_base\\best-v20250402.pt'
SERIAL_PORT = 'COM5'
BAUDRATE = 115200
CAMERA_INDEX = 1
DETECTION_ZONE = [202,107,471,373]
STABILITY_THRESHOLD = 15
STABILITY_FRAMES = 20
DEBUG_MODE = True
HISTORY_FRAMES = 5

# 坐标转换参数
COORD_TRANSFORM = {
    'x_offset': -202,
    'y_offset': -107,
    'x_scale': 0.57621,
    'y_scale': 0.57621,
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