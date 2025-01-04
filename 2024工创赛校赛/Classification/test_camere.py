import cv2
import time

def crop_frame_with_custom_ratio(frame, x_range, y_range):
    """
    按自定义比例裁剪视频帧
    :param frame: 输入的视频帧
    :param x_range: 水平裁剪范围 (start_ratio, end_ratio)，例如 (0.1, 0.9)
    :param y_range: 垂直裁剪范围 (start_ratio, end_ratio)，例如 (0.2, 0.8)
    :return: 裁剪后的帧
    """
    h, w, _ = frame.shape  # 获取原始帧的高和宽
    
    # 计算裁剪区域的边界
    x_start = int(w * x_range[0])
    x_end = int(w * x_range[1])
    y_start = int(h * y_range[0])
    y_end = int(h * y_range[1])

    # 确保范围合法
    x_start = max(0, x_start)
    x_end = min(w, x_end)
    y_start = max(0, y_start)
    y_end = min(h, y_end)

    # 裁剪帧
    cropped_frame = frame[y_start:y_end, x_start:x_end]
    return cropped_frame

# 打开摄像头1（编号为1）
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 设置裁剪范围（相对于原始图像的比例）
x_range = (0.15,0.75)  # 水平方向，从左边的15%到右边的75%
y_range = (0.30,0.80)   # 垂直方向，从上边的30%到下边的80%

print("按 'q' 键退出")

# 设置目标窗口大小
# target_size = (640, 474)
# 添加标志变量，确保图片只保存一次
saved=0

while True:
    # 读取摄像头的一帧
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头画面")
        break

    # 按自定义比例裁剪帧
    cropped_frame = crop_frame_with_custom_ratio(frame, x_range=x_range, y_range=y_range)

    # 调整裁剪后的帧到指定大小
    #resized_frame = cv2.resize(cropped_frame, target_size, interpolation=cv2.INTER_LINEAR)
    # 显示裁剪后的帧
   # cv2.imshow("Cropped and Resized Frame", resized_frame)
    # 保存图片，只执行一次
       # time.sleep(1000)
    # 调整裁剪后的图片大小为 640x480
    resized_frame = cv2.resize(cropped_frame, (640, 480),interpolation=cv2.INTER_LINEAR)

    cv2.imwrite("background.jpg", resized_frame)
    print("图片已保存为 background.jpg")
    saved += 1  # 更新标志变量，防止重复保存
    if saved == 20:
        break

# 释放摄像头资源并关闭窗口
cap.release()
cv2.destroyAllWindows()
