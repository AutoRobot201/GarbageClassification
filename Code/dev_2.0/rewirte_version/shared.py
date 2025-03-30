from PyQt5.QtCore import QObject, pyqtSignal

class Communication(QObject):
    update_count = pyqtSignal(int)      # 分类更新信号
    trigger_detection = pyqtSignal()    # 检测触发信号
    system_stop = pyqtSignal()          # 系统停止信号

shared = Communication()