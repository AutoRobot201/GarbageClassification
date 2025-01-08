import time
import asyncio
import AsyncSerial as async_serial
import Protocol as protocol

async def main(serial,baudrate):
    serial = async_serial.AsyncSerial_t(serial,baudrate)
    serial.startListening(lambda data: serial.write(data))

    result = { # test result
        "class" : 0,
        "center_x" : 34,
        "center_y" : 56
    }

    while True: # 只针对一次投入, 多件垃圾的情况(若是多次投入需再外加循环)
        read_frame = async_serial.AsyncSerial_t.getRawData()
        parsed_frame = protocol.Protocol.parse_frame(read_frame)
        single = protocol.Protocol.handle_command(parsed_frame["command"],parsed_frame["data_bytes"])
        
        # print(single) # --test input

        if single == 'send':
            # get_result
            if result["class"] == 5: # 特殊编号, 5表示已经分类完了 
                print("All subjects have been classified.") # 可替换成PyQt显示
                break
            else:
                send_frame = protocol.Protocol.build_command_0x3001(
                                                                    result["class"],
                                                                    result["center_x"],
                                                                    result["center_y"]
                                                                )
                serial.write(send_frame)
                print(f"Sent frame: {send_frame.hex()}")

            

if __name__ == '__main__':
    asyncio.run(main(serial="COM2",baudrate=115200))