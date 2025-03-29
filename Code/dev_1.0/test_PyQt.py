import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QTextEdit,
    QStackedWidget,
    QLabel
)
from PyQt5.QtCore import Qt

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        
        # 中央部件
        self.central_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)
        
        # 堆叠窗口
        self.stacked_widget = QStackedWidget(self.central_widget)
        
        # 初始化页面
        self.page1 = QWidget()
        self.init_page1()
        
        self.page2 = QWidget()
        self.init_page2()
        
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)
        
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.stacked_widget)

    def init_page1(self):
        layout = QVBoxLayout(self.page1)
        self.start_btn = QPushButton("开始运行", self.page1)
        self.start_btn.setFixedSize(200, 60)
        
        # 按钮样式
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                border: 2px solid #388E3C;
                border-radius: 5px;
                color: white;
                font: bold 16px;
            }
            QPushButton:hover {
                background: #66BB6A;
            }
        """)
        
        layout.addStretch()
        layout.addWidget(self.start_btn, 0, Qt.AlignCenter)
        layout.addStretch()

    def init_page2(self):
        main_layout = QVBoxLayout(self.page2)
        
        # 垃圾分类颜色配置
        class_colors = [
            ("可回收垃圾", "#2196F3"),  # 蓝色
            ("厨余垃圾", "#4CAF50"),    # 绿色
            ("有害垃圾", "#F44336"),    # 红色
            ("其他垃圾", "#9E9E9E")      # 灰色
        ]
        
        # 上半部分四个分类框
        top_layout = QHBoxLayout()
        self.frames = []
        for i in range(4):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setLineWidth(2)
            frame.setFixedSize(180, 120)
            
            # 设置分类颜色和标签
            class_name, color = class_colors[i]
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-color: #607D8B;
                    border-radius: 5px;
                }}
                QLabel {{
                    color: white;
                    font: bold 14px;
                }}
            """)
            
            # 添加分类标签
            label_layout = QVBoxLayout(frame)
            label_layout.addStretch()
            class_label = QLabel(class_name, frame)
            class_label.setAlignment(Qt.AlignCenter)
            label_layout.addWidget(class_label)
            label_layout.addStretch()
            
            top_layout.addWidget(frame)
            self.frames.append(frame)
        
        # 消息框
        self.msg_box = QTextEdit()
        self.msg_box.setStyleSheet("""
            QTextEdit {
                background: #FAFAFA;
                border: 2px solid #B0BEC5;
                font: 14px;
                padding: 10px;
            }
        """)
        self.msg_box.setReadOnly(True)
        
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.msg_box)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 连接信号
        self.ui.start_btn.clicked.connect(self.switch_to_detect)
        
    def switch_to_detect(self):
        self.ui.stacked_widget.setCurrentIndex(1)
        self.append_message("系统启动...")
        
    def append_message(self, msg):
        self.ui.msg_box.append(f"[INFO] {msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("智能垃圾分类系统")
    window.show()
    sys.exit(app.exec_())