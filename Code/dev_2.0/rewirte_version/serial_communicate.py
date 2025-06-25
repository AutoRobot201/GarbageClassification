# serial_communicate.py
import serial
from typing import Optional

class SerialCommunicator:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.serial = self._init_serial()

    def _init_serial(self) -> Optional[serial.Serial]:
        try:
            ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1
            )
            print(f"成功打开串口 {self.port}")
            return ser
        except Exception as e:
            print(f"串口连接失败: {str(e)}")
            return None

    def send_data(self, data: str):
        if self.serial and self.serial.is_open:
            try:
                self.serial.write(data.encode())
                print(f"已发送数据: {data}")
            except Exception as e:
                print(f"串口发送失败: {str(e)}")

    def close(self):
        if self.serial:
            self.serial.close()