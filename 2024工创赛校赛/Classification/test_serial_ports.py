import serial.tools.list_ports
import serial


# ser = serial.Serial('COM5',baudrate=15200,timeout=0.1)

"""
def send_result_serial(cls, center_x, center_y):
    center_x = int(center_x) % 100
    center_y = int(center_y) % 100
    data_str = f"{cls},{center_x},{center_y}\n"
    ser.write(data_str.encode('utf-8'))
    print("已经发送数据:",data_str)
"""

print("Here are the serial ports:")
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device, "-", port.description)

print("")


# send_result_serial(cls=1,center_x=35,center_y=56)

# data = ser.readline().decode('utf-8').strip()
# print(data)