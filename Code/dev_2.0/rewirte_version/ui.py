# ui_main.py
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garbage Sorting System")
        self.setMinimumSize(800, 600)
        
        # 创建堆叠布局
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 初始化页面
        self.init_start_page()
        self.init_detect_page()

    def init_start_page(self):
        """启动页面"""
        start_page = QWidget()
        layout = QVBoxLayout(start_page)
        layout.setContentsMargins(50, 50, 50, 50)

        # 自定义圆角按钮
        self.start_btn = QPushButton("START")
        self.start_btn.setFixedSize(320, 160)
        self.start_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        # 设置按钮样式
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 48px;
                border-radius: 35px;
                border: 4px solid #45a049;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        layout.addStretch()
        layout.addWidget(self.start_btn, 0, Qt.AlignCenter)
        layout.addStretch()
        self.stack.addWidget(start_page)

    def create_bin_widget(self, name, color):
        """创建带标签的垃圾桶部件"""
        container = QWidget()
        container.setFixedSize(160, 180)
        
        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(8)

        # 图标容器
        icon_frame = QFrame()
        icon_frame.setFixedSize(120, 120)
        icon_frame.setStyleSheet(f"""
            background-color: {color};
            border-radius: 20px;
        """)
        
        # 文字标签容器
        label_frame = QFrame(icon_frame)
        label_frame.setGeometry(10, 80, 100, 30)
        label_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 150);
            border-radius: 10px;
        """)
        
        # 标签文字
        label = QLabel(name, label_frame)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
        """)
        label.setGeometry(0, 0, 100, 30)

        vbox.addWidget(icon_frame)
        return container

    def init_detect_page(self):
        """检测页面"""
        detect_page = QWidget()
        main_layout = QVBoxLayout(detect_page)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # 上半部分-垃圾桶图标
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(40)

        # 垃圾桶配置
        bins = [
            ("Recyclable", "#009688"), 
            ("Hazardous", "#F44336"),
            ("Organic", "#8BC34A"),
            ("Residual", "#9E9E9E")
        ]

        for name, color in bins:
            bin_widget = self.create_bin_widget(name, color)
            top_layout.addWidget(bin_widget)

        # 分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                border: 2px solid #cccccc;
                margin: 10px 0;
            }
        """)

        # 下半部分-占位
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("""
            background-color: #f8f9fa;
            border-radius: 15px;
            border: 2px solid #dee2e6;
        """)

        main_layout.addWidget(top_widget)
        main_layout.addWidget(separator)
        main_layout.addWidget(bottom_widget, 1)

        self.stack.addWidget(detect_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())