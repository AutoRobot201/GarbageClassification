import serial
import time

ser = serial.Serial(port='COM6', baudrate=115200)

send_frame = '14000110095'

ser.write(send_frame.encode()) 
print(f"send frame: {send_frame}")

ser.close()