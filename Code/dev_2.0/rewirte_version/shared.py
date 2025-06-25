# shared.py
from PyQt5.QtCore import QObject, pyqtSignal

class Communication(QObject):
    update_count = pyqtSignal(int)
    trigger_detection = pyqtSignal()
    system_stop = pyqtSignal()
    status_info = pyqtSignal(str, str, str)  # 新增状态信号

shared = Communication()