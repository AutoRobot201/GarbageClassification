# 系统配置参数
MODEL_PATH = 'E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\Code\\dev_2.0\\best-v20250330.pt'
SERIAL_PORT = 'COM5'
BAUDRATE = 115200
CAMERA_INDEX = 1
DETECTION_ZONE = [202,107,471,373]
STABILITY_THRESHOLD = 15
STABILITY_FRAMES = 10

# 坐标转换参数
COORD_TRANSFORM = {
    'x_offset': -190,
    'y_offset': -110,
    'x_scale': 0.61884,
    'y_scale': 0.61884,
    'result_offset': (50, 10)
}

# 可视化参数
VISUAL_CONFIG = {
    'box_color': (0, 0, 255),
    'center_color': (255, 0, 255),
    'text_color': (255, 255, 0),
    'box_thickness': 2,
    'center_radius': 5
}