import numpy as np

# 电机坐标 (x_m, y_m)
motor_coords = np.array([[150, 0], [50, 135]])  # 两组电机坐标
# 像素坐标 (x_p, y_p)
pixel_coords = np.array([[154, 33], [524, 396]])  # 对应的像素坐标

# 解线性方程 Ax + B = P
def calculate_linear_mapping(motor_coords, pixel_coords):
    # 拆分电机坐标和像素坐标
    x_m, y_m = motor_coords[:, 0], motor_coords[:, 1]
    x_p, y_p = pixel_coords[:, 0], pixel_coords[:, 1]

    # 求解 X 轴的 A_x 和 B_x
    A_x = (x_p[0] - x_p[1]) / (x_m[0] - x_m[1])
    B_x = x_p[0] - A_x * x_m[0]

    # 求解 Y 轴的 A_y 和 B_y
    A_y = (y_p[0] - y_p[1]) / (y_m[0] - y_m[1])
    B_y = y_p[0] - A_y * y_m[0]

    return (A_x, B_x), (A_y, B_y)

# 计算映射参数
(x_params, y_params) = calculate_linear_mapping(motor_coords, pixel_coords)
A_x, B_x = x_params
A_y, B_y = y_params

print(f"X 轴映射参数: A_x = {A_x}, B_x = {B_x}")
print(f"Y 轴映射参数: A_y = {A_y}, B_y = {B_y}")

# 映射函数：电机坐标 -> 像素坐标
def motor_to_pixel(motor_coord, x_params, y_params):
    x_m, y_m = motor_coord
    A_x, B_x = x_params
    A_y, B_y = y_params

    x_p = A_x * x_m + B_x
    y_p = A_y * y_m + B_y

    return x_p, y_p

# 逆向映射函数：像素坐标 -> 电机坐标
def pixel_to_motor(pixel_coord, x_params, y_params):
    x_p, y_p = pixel_coord
    A_x, B_x = x_params
    A_y, B_y = y_params

    # 逆向计算
    x_m = (x_p - B_x) / A_x
    y_m = (y_p - B_y) / A_y

    return x_m, y_m

# 测试正向映射
test_motor_coord = (100, 50)  # 输入电机坐标
predicted_pixel_coord = motor_to_pixel(test_motor_coord, x_params, y_params)
print(f"电机坐标 {test_motor_coord} 映射到像素坐标: {predicted_pixel_coord}")

# 测试逆向映射
test_pixel_coord = (166.5,177.5)  # 输入像素坐标
predicted_motor_coord = pixel_to_motor(test_pixel_coord, x_params, y_params)
print(f"像素坐标 {test_pixel_coord} 映射到电机坐标: {predicted_motor_coord}")
