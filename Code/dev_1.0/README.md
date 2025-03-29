### <center>2025年工程创新大赛</center>

#### 1.文件结构
.
├── main.py # 主程序入口
├── config.py # 系统配置参数
├── detector.py # 目标检测模块
├── tracker.py # 物体追踪模块
|—— AsyncSerial.py # 异步通信库,用于优化通信
|—— Protocol.py # 通信库,包含了格式化通信的方法
|—— testPyQt.py # PyQt的测试代码
|—— examplemain.py # 示例程序(用于演示如何使用Async和Protocol库)
|—— garbage.pt # YOLOv11权重文件(2024-12版)
└── visualizer.py # 可视化模块


#### 模块说明

##### 1. config.py
- **功能**: 集中管理系统所有配置参数
- **包含参数**:
  - 模型路径
  - 摄像头设置
  - 检测区域坐标
  - 稳定性判断阈值
  - 帧率控制参数
  - 显示样式设置

##### 2. detector.py
- **核心类**: `Detector`
- **功能**:
  - 加载YOLO模型
  - 执行目标检测
  - 解析检测结果
- **主要方法**:
  - `detect()`: 执行图像检测
  - `_parse_results()`: 解析模型输出

##### 3. tracker.py
- **核心类**: `ObjectTracker`
- **功能**:
  - 物体ID分配与追踪
  - 位置稳定性计算
  - 物体状态维护
- **关键方法**:
  - `update()`: 更新追踪状态
  - `get_stable_objects()`: 获取稳定物体

##### 4. visualizer.py
- **核心类**: `Visualizer`
- **功能**:
  - 绘制检测区域
  - 显示物体追踪信息
  - 画面输出控制
- **主要方法**:
  - `draw_detection_zone()`: 绘制检测区域
  - `draw_tracking_info()`: 显示物体信息

##### 5. main.py
- **系统流程**:
  1. 初始化摄像头和模块
  2. 帧率控制
  3. 图像采集
  4. 目标检测
  5. 物体追踪
  6. 稳定性判断
  7. 可视化输出
  8. 资源释放

#### 运行要求
- Python 3.8+
- 依赖库:
  - ultralytics
  - opencv-python
  - numpy

#### 使用说明
1. 安装依赖: `pip install ultralytics opencv-python numpy`
2. 放置训练好的YOLO模型到指定路径
3. 运行主程序: `python main.py`
4. 按Q键退出程序