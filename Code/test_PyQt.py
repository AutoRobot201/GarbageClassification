# This is a script for test

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("PyQt5 测试")
label = QLabel("环境配置成功！", parent=window)
label.move(50, 50)
window.show()
sys.exit(app.exec_())
