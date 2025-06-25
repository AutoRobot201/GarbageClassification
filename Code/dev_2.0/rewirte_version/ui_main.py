# ui.py
import cv2
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from shared import shared
# from main import number_counter
import main
import detector
from config import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.counts = [0, 0, 0, 0]  # 可回收物, 有害垃圾, 厨余垃圾, 其他垃圾
        self.video_capture = None
        self.video_timer = QTimer(self)
        self.init_ui()
        self.start_detection_thread()
        self.video_timer.timeout.connect(self.update_video_frame)

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("智能垃圾分类系统 v2025-04")
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("background-color: #f5f6fa;")

        # 主堆叠布局
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 初始化页面
        self.init_start_page()
        self.init_detect_page()
        self.setup_video()

    def setup_video(self):
        """初始化视频播放组件"""
        if self.video_capture:
            self.video_capture.release()
        
        # 加载宣传视频（请修改为实际路径）
        self.video_capture = cv2.VideoCapture('E:\\Code\\NJUST-AutoRobot\\GarbageClassification\\Code\\dev_2.0\\rewirte_version\\video.mp4')
        if self.video_capture.isOpened():
            self.video_timer.start(30)
        else:
            print("无法加载宣传视频")

    def init_start_page(self):
        """启动页面初始化"""
        start_page = QWidget()
        main_layout = QHBoxLayout(start_page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 视频区域 (左侧2/3)
        video_widget = QWidget()
        video_widget.setStyleSheet("background-color: #000000;")
        video_layout = QVBoxLayout(video_widget)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        video_layout.addWidget(self.video_label)
        main_layout.addWidget(video_widget, 2)

        # 右侧控制面板 (1/3)
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #f5f6fa;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setSpacing(40)

        # 系统标题
        title_label = QLabel("垃圾分类检测系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        # 启动按钮
        self.start_btn = QPushButton("开始检测")
        self.start_btn.setFixedSize(320, 160)
        self.start_btn.clicked.connect(self.switch_to_detect_page)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 36px;
                border-radius: 35px;
                border: 3px solid #45a049;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        right_layout.addStretch()
        right_layout.addWidget(title_label)
        right_layout.addWidget(self.start_btn, 0, Qt.AlignCenter)
        right_layout.addStretch()

        main_layout.addWidget(right_panel, 1)
        self.stack.addWidget(start_page)

    def init_detect_page(self):
        """检测页面初始化"""
        detect_page = QWidget()
        main_layout = QVBoxLayout(detect_page)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # 状态栏
        self.status_label = QLabel("系统准备就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #2c3e50;
                padding: 12px;
                background-color: #ecf0f1;
                border-radius: 8px;
                border: 1px solid #dcdde1;
            }
        """)

        # 主体内容布局
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # 视频显示区域
        video_widget = QWidget()
        video_layout = QVBoxLayout(video_widget)
        self.detect_video_label = QLabel()
        self.detect_video_label.setAlignment(Qt.AlignCenter)
        self.detect_video_label.setStyleSheet("""
            background-color: #000;
            border-radius: 10px;
            border: 2px solid #666;
        """)
        video_layout.addWidget(self.detect_video_label)

        # 右侧信息面板
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(20)

        # 分类统计标题
        stats_title = QLabel("分类统计")
        stats_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #2c3e50;
                font-weight: bold;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }
        """)

        # 分类统计容器
        stats_container = QWidget()
        stats_grid = QGridLayout(stats_container)
        stats_grid.setContentsMargins(0, 0, 0, 0)
        stats_grid.setSpacing(20)

        # 分类条目
        bins = [
            ("可回收物", "#009688", 0),
            ("有害垃圾", "#F44336", 1),
            ("厨余垃圾", "#8BC34A", 2),
            ("其他垃圾", "#9E9E9E", 3)
        ]
        for idx, (name, color, _) in enumerate(bins):
            bin_widget = self.create_bin_widget(name, color, idx)
            stats_grid.addWidget(bin_widget, idx//2, idx%2)

        # 控制按钮
        self.reset_btn = QPushButton("重置计数器")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.clicked.connect(self.reset_counts)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                border-radius: 6px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        # 组装布局
        info_layout.addWidget(stats_title)
        info_layout.addWidget(stats_container)

        # 实时垃圾信息面板
        info_group = QGroupBox("垃圾状态")
        info_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        info_grid = QGridLayout()
        
        # 创建信息标签
        self.garbage_info_labels = {
            'type_num': QLabel("0"),
            'type_text': QLabel("---"),
            'status': QLabel("1"),
            'load': QLabel("OK")
        }
        
        # 设置标签样式
        for label in self.garbage_info_labels.values():
            label.setStyleSheet("font-size: 16px; color: #2c3e50;")
            label.setAlignment(Qt.AlignRight)
        
        # 添加标签到网格
        info_grid.addWidget(QLabel("序号:"), 0, 0)
        info_grid.addWidget(self.garbage_info_labels['type_num'], 0, 1)
        info_grid.addWidget(QLabel("垃圾类型:"), 1, 0)
        info_grid.addWidget(self.garbage_info_labels['type_text'], 1, 1)
        info_grid.addWidget(QLabel("垃圾数量:"), 2, 0)
        info_grid.addWidget(self.garbage_info_labels['status'], 2, 1)
        info_grid.addWidget(QLabel("状态:"), 3, 0)
        info_grid.addWidget(self.garbage_info_labels['load'], 3, 1)
        
        info_group.setLayout(info_grid)
        info_layout.addWidget(info_group)


        info_layout.addWidget(self.reset_btn)
        info_layout.addStretch()

        content_layout.addWidget(video_widget, 3)
        content_layout.addWidget(info_widget, 1)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(content_widget)

        self.stack.addWidget(detect_page)

    
    def update_garbage_info(self, cls_index):
        """更新垃圾信息显示"""
        type_mapping = {
            0: ("0", "可回收物"),
            1: ("1", "有害垃圾"),
            2: ("2", "厨余垃圾"),
            3: ("3", "其他垃圾")
        }
        
        if cls_index in type_mapping:
            num, text = type_mapping[cls_index]
            self.garbage_info_labels['type_num'].setText(str(main.number_counter))
            print("NUMBER_COUNTER = ",main.number_counter)
            self.garbage_info_labels['type_text'].setText(text)
            self.garbage_info_labels['status'].setText("1")
            self.garbage_info_labels['load'].setText("OK")

    def create_bin_widget(self, name, color, index):
        """创建分类统计条目"""
        container = QWidget()
        container.setFixedSize(240, 100)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)

        color_label = QLabel()
        color_label.setFixedSize(36, 36)
        color_label.setStyleSheet(f"""
            background-color: {color};
            border-radius: 18px;
            border: 2px solid #fff;
        """)

        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(10, 0, 0, 0)
        
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 16px; color: #34495e; font-weight: 500;")
        
        count_label = QLabel("0")
        count_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        setattr(self, f"count_label_{index}", count_label)
        
        text_layout.addWidget(name_label)
        text_layout.addWidget(count_label)
        text_layout.addStretch()

        layout.addWidget(color_label)
        layout.addWidget(text_widget)
        return container

    def start_detection_thread(self):
        """启动检测线程"""
        self.thread = QThread()
        self.worker = DetectionWorker()
        self.worker.moveToThread(self.thread)

        self.worker.system.trigger_request.connect(self.worker.system.start_detection_trigger)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.system.frame_ready.connect(self.update_detect_frame)
        self.worker.system.status_changed.connect(self.update_status)
        self.worker.system.detection_result.connect(self.handle_detection)
        shared.update_count.connect(self.update_count)

        self.thread.start()

    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.stack.currentIndex() == 1:
                self.worker.system.trigger_request.emit()
                self.status_label.setText("🔄 检测已触发...")
        elif event.key() == Qt.Key_Escape:
            self.stack.setCurrentIndex(0)
        super().keyPressEvent(event)

    def update_video_frame(self):
        """更新启动页视频"""
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.video_label.setPixmap(pixmap.scaled(
                self.video_label.size(), 
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

    def update_detect_frame(self, image):
        """更新检测页视频"""
        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(
            self.detect_video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.detect_video_label.setPixmap(scaled_pixmap)

    def handle_detection(self, detected):
        """处理检测结果"""
        cls_index = 0
        if detected:
             # 获取第一个检测目标的信息
            first_obj = detected[0]
            cls_index = first_obj[1]
        elif detector.time_outs >= TIMEOUT_THRESHOLD: 
            cls_index = 0
        
        # 更新垃圾信息显示
        self.update_garbage_info(cls_index)
            
        pixmap = self.detect_video_label.pixmap()
        if pixmap:
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
                
            for obj in detected:
                _, cls, cx, cy, x1, y1, x2, y2 = obj
                    
                # 绘制边界框
                pen = QPen(QColor(255, 0, 0), 2)
                painter.setPen(pen)
                painter.drawRect(x1, y1, x2-x1, y2-y1)
                    
                # 绘制中心点
                painter.setBrush(QColor(0, 0, 255))
                painter.drawEllipse(QPoint(cx, cy), 3, 3)
                    
            painter.end()
            self.detect_video_label.setPixmap(pixmap)

    def update_status(self, status):
        self.status_label.setText(status)

    def update_count(self, cls_index):
        if 0 <= cls_index <= 3:
            self.counts[cls_index] += 1
            label = getattr(self, f"count_label_{cls_index}")
            label.setText(str(self.counts[cls_index]))
            label.setStyleSheet("color: #e74c3c;")
            QTimer.singleShot(300, lambda: label.setStyleSheet("color: #2c3e50;"))

    def reset_counts(self):
        self.counts = [0, 0, 0, 0]
        for i in range(4):
            getattr(self, f"count_label_{i}").setText("0")
        self.status_label.setText("计数器已重置")

    def switch_to_detect_page(self):
        self.stack.setCurrentIndex(1)
        self.worker.system.trigger_request.emit()
        #shared.trigger_detection.emit()

    def closeEvent(self, event):
        shared.system_stop.emit()
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(2000)
        event.accept()

class DetectionWorker(QObject):
    finished = pyqtSignal()
    system = None

    def __init__(self):
        super().__init__()
        self.system = main.GarbageDetectionSystem()

    def run(self):
        self.system.start_detection()
        self.finished.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())