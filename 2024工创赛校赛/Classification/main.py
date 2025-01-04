import time

from detect import run, parse_opt, result_list_yolo
from hardware import ClassificationFunction

CF = ClassificationFunction(serial_port="COM11", baud_rate=9600)

def main(opt):
    # check_requirements(ROOT / "requirements.txt", exclude=("tensorboard", "thop"))
    
    cap_number = 1 # 0 reminds Windows-Camera , 1 remind another camera.

    while True:
        data = CF.ser.readline().decode('utf-8').strip()
        if data == 'start':
            CF.take_photo(cap_number=1)
            run(**vars(opt))
            CF.result_list = result_list_yolo
            # CF.result_list.sort(key=lambda x: x.s, reverse=True)
            # CF.create_test_data()

            for result in CF.result_list:
                data = CF.ser.readline().decode('utf-8').strip()
                time.sleep(CF.interval_sent)
                CF.send_result_serial(result.cls,result.cx,result.cy)
                while data != 'rec':
                    data = CF.ser.readline().decode('utf-8').strip()
                    print(f"while-rec: {data}")

                while data != 'next':
                    data = CF.ser.readline().decode('utf-8').strip()
                    time.sleep(CF.interval_sent)
                    print(f"while-next: {data}")
                    print("We have received the command,but it is a wrong command, we need a \'next\'.")
                
            CF.result_list.clear()
            CF.send_introduction()
            print("All objects in this image have been clasified.")
            
        else:
            print("We have received the command,but it is a wrong command, we need a \'start\'.")


if __name__ == '__main__':
    opt = parse_opt()
    main(opt)