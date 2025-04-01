# ui.py
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from shared import shared
import main

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.counts = [0, 0, 0, 0]  # 可回收物, 有害垃圾, 厨余垃圾, 其他垃圾
        self.init_ui()
        self.start_detection_thread()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("智能垃圾分类系统 v2.2")
        self.setMinimumSize(1280, 720)
        self.setStyleSheet("background-color: #f5f6fa;")

        # 主堆叠布局
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 初始化页面
        self.init_start_page()
        self.init_detect_page()

    def init_start_page(self):
        """启动页面初始化"""
        start_page = QWidget()
        layout = QVBoxLayout(start_page)
        layout.setContentsMargins(50, 50, 50, 50)

        # 系统标题
        title_label = QLabel("垃圾分类检测系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #2c3e50;
                font-weight: bold;
                margin-bottom: 40px;
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

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(self.start_btn, 0, Qt.AlignCenter)
        layout.addStretch()
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
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            background-color: #000;
            border-radius: 10px;
            border: 2px solid #666;
        """)
        video_layout.addWidget(self.video_label)

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

        # 组装右侧面板
        info_layout.addWidget(stats_title)
        info_layout.addWidget(stats_container)
        info_layout.addWidget(self.reset_btn)
        info_layout.addStretch()

        # 组装主布局
        content_layout.addWidget(video_widget, 3)
        content_layout.addWidget(info_widget, 1)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(content_widget)

        self.stack.addWidget(detect_page)

    def create_bin_widget(self, name, color, index):
        """创建分类统计条目"""
        container = QWidget()
        container.setFixedSize(240, 100)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)

        # 颜色标识
        color_label = QLabel()
        color_label.setFixedSize(36, 36)
        color_label.setStyleSheet(f"""
            background-color: {color};
            border-radius: 18px;
            border: 2px solid #fff;
        """)

        # 文字信息
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

        # 信号连接
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.system.frame_ready.connect(self.update_video_frame)
        self.worker.system.status_changed.connect(self.update_status)
        self.worker.system.detection_result.connect(self.handle_detection)
        shared.update_count.connect(self.update_count)
        shared.trigger_detection.connect(self.worker.system.start_detection_trigger)

        self.thread.start()

    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.stack.currentIndex() == 1:
                shared.trigger_detection.emit()
                self.status_label.setText("🔄 检测已触发...")
        elif event.key() == Qt.Key_Escape:
            self.stack.setCurrentIndex(0)
        super().keyPressEvent(event)

    def update_video_frame(self, image):
        """更新视频画面"""
        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def handle_detection(self, detected):
        """处理检测结果并绘制标注"""
        if detected:
            # 在现有视频帧上绘制
            pixmap = self.video_label.pixmap()
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
                    painter.setBrush(QColor(255, 0, 255))
                    painter.drawEllipse(QPoint(cx, cy), 5, 5)
                    
                    # 绘制类别标签
                    painter.setFont(QFont("Microsoft YaHei", 12))
                    painter.drawText(x1+10, y1+30, f"类别: {cls}")

                painter.end()
                self.video_label.setPixmap(pixmap)

    def update_status(self, status):
        """更新状态栏"""
        self.status_label.setText(status)

    def update_count(self, cls_index):
        """更新分类计数"""
        if 0 <= cls_index <= 3:
            # print(f"种类：{cls_index}")
            self.counts[cls_index] += 1
            label = getattr(self, f"count_label_{cls_index}")
            label.setText(str(self.counts[cls_index]))
            # 添加颜色动画
            label.setStyleSheet("color: #e74c3c;")
            QTimer.singleShot(300, lambda: label.setStyleSheet("color: #2c3e50;"))

    def reset_counts(self):
        """重置所有计数器"""
        self.counts = [0, 0, 0, 0]
        for i in range(4):
            label = getattr(self, f"count_label_{i}")
            label.setText("0")
        self.status_label.setText("计数器已重置")

    def switch_to_detect_page(self):
        """切换到检测页面"""
        self.stack.setCurrentIndex(1)
        shared.trigger_detection.emit()  # 自动开始检测

    def closeEvent(self, event):
        """处理窗口关闭事件"""
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
        """启动检测系统"""
        self.system.start_detection()
        self.finished.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置全局字体
    font = QFont()
    font.setFamily("Microsoft YaHei")
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())